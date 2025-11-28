package handlers

import (
	"bytes"
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

// MockRegistrationManager реализует интерфейс database.RegistrationManager для тестов.
type MockRegistrationManager struct {
	mock.Mock
}

func (m *MockRegistrationManager) RegistrateUser(login, password, fio string) (*uuid.UUID, error) {
	args := m.Called(login, password, fio)

	// Обрабатываем случай когда возвращается nil UUID
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*uuid.UUID), args.Error(1)
}

func Test_RegHandler(t *testing.T) {
	logger := logrus.New()
	secret := "test-secret-key"
	testUUID := uuid.New()

	tests := []struct {
		name           string
		setupMocks     func(*MockRegistrationManager)
		requestBody    string
		expectedStatus int
		expectedBody   string
		checkJWT       bool
	}{
		{
			name: "Успешная регистрация",
			setupMocks: func(mrm *MockRegistrationManager) {
				mrm.On("RegistrateUser", "testuser", "testpassword", "Test User").
					Return(&testUUID, nil)
			},
			requestBody:    `{"login":"testuser","password":"testpassword","username":"Test User"}`,
			expectedStatus: http.StatusOK,
			checkJWT:       true,
		},
		{
			name: "Ошибка - пользователь уже существует",
			setupMocks: func(mrm *MockRegistrationManager) {
				mrm.On("RegistrateUser", "existinguser", "password123", "Existing User").
					Return(nil, assert.AnError)
			},
			requestBody:    `{"login":"existinguser","password":"password123","username":"Existing User"}`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"assert.AnError general error for testing","error":"fail registration"}`,
		},
		{
			name: "Ошибка - невалидный JSON",
			setupMocks: func(mrm *MockRegistrationManager) {
				// Мок не должен вызываться при ошибке парсинга JSON
			},
			requestBody:    `{"login": "invalid json`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"unexpected end of JSON input","error":"Invalid JSON format"}`,
		},
		{
			name: "Ошибка - пустое тело запроса",
			setupMocks: func(mrm *MockRegistrationManager) {
				// Мок не должен вызываться при ошибке парсинга JSON
			},
			requestBody:    "",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"unexpected end of JSON input","error":"Invalid JSON format"}`,
		},
		{
			name: "Ошибка - отсутствует логин",
			setupMocks: func(mrm *MockRegistrationManager) {
				// Мок не должен вызываться при отсутствии обязательных полей
			},
			requestBody:    `{"password":"testpassword","username":"Test User"}`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"No login in body"}`,
		},
		{
			name: "Ошибка - отсутствует пароль",
			setupMocks: func(mrm *MockRegistrationManager) {
				// Мок не должен вызываться при отсутствии обязательных полей
			},
			requestBody:    `{"login":"testuser","username":"Test User"}`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"No password in body"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание мока RegistrationManager
			registrationManager := new(MockRegistrationManager)

			// Настройка моков
			tt.setupMocks(registrationManager)

			// Создание Fiber приложения и обработчика
			app := fiber.New()
			regHandler := NewReg(registrationManager, secret, logger)

			app.Post("/register", regHandler.Handler)

			// Создание тестового запроса
			req := httptest.NewRequest(http.MethodPost, "/register", bytes.NewBufferString(tt.requestBody))
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
				// Проверка успешной регистрации с JWT токеном
				var regResponse regOut
				err := json.Unmarshal([]byte(body), &regResponse)
				assert.NoError(t, err)
				assert.NotEmpty(t, regResponse.Jwt)

				// Проверяем что JWT имеет правильную структуру
				jwtParts := strings.Split(regResponse.Jwt, ".")
				assert.Equal(t, 3, len(jwtParts), "JWT должен состоять из 3 частей")
				assert.True(t, len(jwtParts[0]) > 0, "JWT header не должен быть пустым")
				assert.True(t, len(jwtParts[1]) > 0, "JWT payload не должен быть пустым")
				assert.True(t, len(jwtParts[2]) > 0, "JWT signature не должен быть пустым")

				// Декодируем и проверяем JWT payload
				claims := decodeJWTPayload(t, regResponse.Jwt)

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
					"jwt": regResponse.Jwt,
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
			registrationManager.AssertExpectations(t)
		})
	}
}
