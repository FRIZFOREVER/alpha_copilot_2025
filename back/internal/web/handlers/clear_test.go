package handlers

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
)

func Test_ClearHandler(t *testing.T) {
	logger := logrus.New()
	testUUID := uuid.New()

	tests := []struct {
		name           string
		setupMocks     func(*MockHistoryRepository)
		chatIDParam    string
		expectedStatus int
		expectedBody   string
	}{
		{
			name: "Успешная очистка истории чата",
			setupMocks: func(mhr *MockHistoryRepository) {
				mhr.On("CheckChat", testUUID.String(), 123).
					Return(true, nil)
				mhr.On("HideMessages", 123).
					Return(nil)
			},
			chatIDParam:    "123",
			expectedStatus: http.StatusOK,
			expectedBody:   "",
		},
		{
			name: "Ошибка - невалидный формат ID чата",
			setupMocks: func(mhr *MockHistoryRepository) {
				// Мок не должен вызываться при невалидном ID
			},
			chatIDParam:    "invalid",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Invalid chat ID format"}`,
		},
		{
			name: "Ошибка - чат не принадлежит пользователю",
			setupMocks: func(mhr *MockHistoryRepository) {
				mhr.On("CheckChat", testUUID.String(), 456).
					Return(false, nil)
			},
			chatIDParam:    "456",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Chat ID is not corresponds to user uuid"}`,
		},
		{
			name: "Ошибка проверки принадлежности чата",
			setupMocks: func(mhr *MockHistoryRepository) {
				mhr.On("CheckChat", testUUID.String(), 789).
					Return(false, assert.AnError)
			},
			chatIDParam:    "789",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Chat ID is not corresponds to user uuid"}`,
		},
		{
			name: "Ошибка базы данных при очистке истории",
			setupMocks: func(mhr *MockHistoryRepository) {
				mhr.On("CheckChat", testUUID.String(), 999).
					Return(true, nil)
				mhr.On("HideMessages", 999).
					Return(assert.AnError)
			},
			chatIDParam:    "999",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"` + assert.AnError.Error() + `","error":"Error in database"}`,
		},
		{
			name: "Успешная очистка с большим ID чата",
			setupMocks: func(mhr *MockHistoryRepository) {
				mhr.On("CheckChat", testUUID.String(), 999999999).
					Return(true, nil)
				mhr.On("HideMessages", 999999999).
					Return(nil)
			},
			chatIDParam:    "999999999",
			expectedStatus: http.StatusOK,
			expectedBody:   "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание мока HistoryRepository
			historyRepo := new(MockHistoryRepository)

			// Настройка моков
			tt.setupMocks(historyRepo)

			// Создание Fiber приложения и обработчика
			app := fiber.New()
			clearHandler := NewClear(historyRepo, logger)

			// Добавляем middleware для установки UUID в контекст
			app.Use(func(c *fiber.Ctx) error {
				c.Locals("uuid", testUUID)
				return c.Next()
			})

			// Регистрируем маршрут
			app.Delete("/chats/:chat_id/clear", clearHandler.Handler)

			// Создание тестового запроса
			req := httptest.NewRequest(http.MethodDelete, "/chats/"+tt.chatIDParam+"/clear", nil)

			// Выполнение запроса
			resp, err := app.Test(req, -1)
			assert.NoError(t, err)
			defer func() {
				assert.NoError(t, resp.Body.Close())
			}()

			// Проверка статуса ответа
			assert.Equal(t, tt.expectedStatus, resp.StatusCode)

			// Чтение и проверка тела ответа
			body := readBody(t, resp)
			assert.Equal(t, tt.expectedBody, body)

			// Проверка вызовов моков
			historyRepo.AssertExpectations(t)
		})
	}
}
