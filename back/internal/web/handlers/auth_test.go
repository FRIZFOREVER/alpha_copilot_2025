//nolint:errcheck,thelper
package handlers

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockAuthenticator реализует интерфейс database.Authenticator для тестов.
type MockAuthenticator struct {
	mock.Mock
}

func (m *MockAuthenticator) AuthenticateUser(login, password string) (*uuid.UUID, error) {
	args := m.Called(login, password)

	// Обрабатываем случай когда возвращается nil UUID
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*uuid.UUID), args.Error(1)
}

// decodeJWTPayload декодирует payload часть JWT токена.
func decodeJWTPayload(t *testing.T, jwtToken string) map[string]interface{} {
	parts := strings.Split(jwtToken, ".")
	if len(parts) != 3 {
		t.Fatalf("Invalid JWT token structure")
	}

	// Декодируем payload часть (parts[1])
	payload, err := base64.RawURLEncoding.DecodeString(parts[1])
	if err != nil {
		t.Fatalf("Failed to decode JWT payload: %v", err)
	}

	var claims map[string]interface{}
	err = json.Unmarshal(payload, &claims)
	if err != nil {
		t.Fatalf("Failed to unmarshal JWT claims: %v", err)
	}

	return claims
}

func Test_AuthHandler(t *testing.T) {
	logger := logrus.New()
	secret := "test-secret-key"
	testUUID := uuid.New()

	tests := []struct {
		name           string
		setupMocks     func(*MockAuthenticator)
		requestBody    string
		expectedStatus int
		expectedBody   string
		checkJWT       bool
	}{
		{
			name: "Успешная аутентификация",
			setupMocks: func(ma *MockAuthenticator) {
				ma.On("AuthenticateUser", "testuser", "testpassword").
					Return(&testUUID, nil)
			},
			requestBody:    `{"login":"testuser","password":"testpassword"}`,
			expectedStatus: http.StatusOK,
			checkJWT:       true,
		},
		{
			name: "Ошибка - неверные учетные данные",
			setupMocks: func(ma *MockAuthenticator) {
				ma.On("AuthenticateUser", "wronguser", "wrongpassword").
					Return(nil, assert.AnError)
			},
			requestBody:    `{"login":"wronguser","password":"wrongpassword"}`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"assert.AnError general error for testing","error":"fail authentication"}`,
		},
		{
			name: "Ошибка - невалидный JSON",
			setupMocks: func(ma *MockAuthenticator) {
				// Мок не должен вызываться при ошибке парсинга JSON
			},
			requestBody:    `{"login": "invalid json`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"unexpected end of JSON input","error":"Invalid JSON format"}`,
		},
		{
			name: "Ошибка - пустое тело запроса",
			setupMocks: func(ma *MockAuthenticator) {
				// Мок не должен вызываться при ошибке парсинга JSON
			},
			requestBody:    "",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"unexpected end of JSON input","error":"Invalid JSON format"}`,
		},
		{
			name: "Ошибка - пустые логин и пароль",
			setupMocks: func(ma *MockAuthenticator) {
				ma.On("AuthenticateUser", "", "").
					Return(nil, assert.AnError)
			},
			requestBody:    `{"login":"","password":""}`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"assert.AnError general error for testing","error":"fail authentication"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание мока Authenticator
			authenticator := new(MockAuthenticator)

			// Настройка моков
			tt.setupMocks(authenticator)

			// Создание Fiber приложения и обработчика
			app := fiber.New()
			authHandler := NewAuth(authenticator, secret, logger)

			app.Post("/auth", authHandler.Handler)

			// Создание тестового запроса
			req := httptest.NewRequest(http.MethodPost, "/auth", bytes.NewBufferString(tt.requestBody))
			req.Header.Set("Content-Type", "application/json")

			// Выполнение запроса
			resp, err := app.Test(req, -1)
			assert.NoError(t, err)
			defer func() {
				assert.NoError(t, resp.Body.Close())
			}()

			// Проверка статуса ответа
			assert.Equal(t, tt.expectedStatus, resp.StatusCode)

			// Чтение тела ответа
			body := readBody(t, resp)

			if tt.checkJWT {
				// Проверка успешной аутентификации с JWT токеном
				var authResponse authOut
				err := json.Unmarshal([]byte(body), &authResponse)
				assert.NoError(t, err)
				assert.NotEmpty(t, authResponse.Jwt)

				// Проверяем что JWT имеет правильную структуру
				jwtParts := strings.Split(authResponse.Jwt, ".")
				assert.Equal(t, 3, len(jwtParts), "JWT должен состоять из 3 частей")
				assert.True(t, len(jwtParts[0]) > 0, "JWT header не должен быть пустым")
				assert.True(t, len(jwtParts[1]) > 0, "JWT payload не должен быть пустым")
				assert.True(t, len(jwtParts[2]) > 0, "JWT signature не должен быть пустым")

				// Декодируем и проверяем JWT payload
				claims := decodeJWTPayload(t, authResponse.Jwt)

				// Проверяем что UUID в claims соответствует ожидаемому
				uuidClaim, exists := claims["uuid"]
				assert.True(t, exists, "JWT должен содержать claim 'uuid'")
				assert.Equal(t, testUUID.String(), uuidClaim, "UUID в JWT должен соответствовать UUID пользователя")

				// Проверяем наличие стандартных claims
				_, expExists := claims["exp"]
				assert.True(t, expExists, "JWT должен содержать claim 'exp'")

				_, iatExists := claims["iat"]
				assert.True(t, iatExists, "JWT должен содержать claim 'iat'")

				// Проверяем структуру JSON ответа
				expectedJSON := map[string]interface{}{
					"jwt": authResponse.Jwt,
				}
				var actualJSON map[string]interface{}
				err = json.Unmarshal([]byte(body), &actualJSON)
				assert.NoError(t, err)
				assert.Equal(t, expectedJSON, actualJSON)
			} else {
				// Проверка тела ответа для ошибок
				assert.Equal(t, tt.expectedBody, body)
			}

			// Проверка вызовов моков
			authenticator.AssertExpectations(t)
		})
	}
}
