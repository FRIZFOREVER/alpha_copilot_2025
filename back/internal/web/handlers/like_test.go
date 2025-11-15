package handlers

import (
	"bytes"
	"io"
	"jabki/internal/settings"
	"jabki/internal/web/middlewares"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/golang-jwt/jwt/v5"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockLikeRepository struct {
	mock.Mock
}

func (m *MockLikeRepository) CheckChat(userUUID string, chatID int) (bool, error) {
	args := m.Called(userUUID, chatID)
	return args.Get(0).(bool), args.Error(1)
}

func (m *MockLikeRepository) SetLike(chatID int, answerID int, rating *int) error {
	args := m.Called(chatID, answerID, rating)
	return args.Error(0)
}

func TestConfig_Change(t *testing.T) {
	logger := logrus.New()
	settings := settings.InitSettings(logger)
	tests := []struct {
		name             string
		chatID           string
		httpMethod       string
		body             []byte
		setupMocks       func(*MockLikeRepository)
		expectedStatus   int
		expectedResponse string
	}{
		{
			name:       "1) Запрос на оценивание ответа",
			chatID:     "1",
			httpMethod: fiber.MethodPut,
			body:       []byte(`{"answer_id": 2,"rating": 5}`),
			setupMocks: func(mr *MockLikeRepository) {
				rating := 5
				mr.On("CheckChat", "00000000-0000-0000-0000-000000000000", 1).Return(true, nil)
				mr.On("SetLike", 1, 2, &rating).Return(nil)
			},
			expectedStatus:   fiber.StatusOK,
			expectedResponse: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание моков.
			repo := new(MockLikeRepository)

			// Настройка моков.
			tt.setupMocks(repo)

			// Создание сервиса и контроллера.

			app := fiber.New()

			authMiddleware := middlewares.NewUserAuthentication(settings.SecretUser, logger)
			app.Use(middlewares.Cors(settings.FrontOrigin), authMiddleware.Handler)
			like := NewLike(repo, logger)
			app.Put("/like/:chat_id", like.Handler)

			token, err := generateTokenForTest(settings.SecretUser)
			assert.NoError(t, err)

			// Готовим запрос.
			req := httptest.NewRequest(tt.httpMethod, "/like/"+tt.chatID, bytes.NewReader(tt.body))
			req.Header.Set("Authorization", "Bearer "+token)

			// Выполняем тестовый запрос.
			resp, err := app.Test(req, -1)
			if err != nil {
				t.Fatalf("Failed to test request: %v", err)
			}
			defer func() {
				assert.NoError(t, resp.Body.Close())
			}()

			// Проверяем статус ответа.
			assert.Equal(t, tt.expectedStatus, resp.StatusCode)

			// Читаем тело ответа.
			body, err := io.ReadAll(resp.Body)
			assert.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, resp.StatusCode)
			assert.Equal(t, tt.expectedResponse, string(body))

			// Проверка, что все ожидаемые вызовы были выполнены.

			repo.AssertExpectations(t)
		})
	}
}

func generateTokenForTest(secret string) (string, error) {
	claims := jwt.MapClaims{
		"exp":  time.Now().Add(time.Hour * 24).Unix(),
		"uuid": "00000000-0000-0000-0000-000000000000",
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(secret))
	if err != nil {
		return "", err
	}

	return tokenString, nil
}
