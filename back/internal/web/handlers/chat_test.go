package handlers

import (
	"bytes"
	"jabki/internal/database"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockChatManager реализует интерфейс database.ChatManager для тестов.
type MockChatManager struct {
	mock.Mock
}

func (m *MockChatManager) CreateChat(chatName string, userUUID string) (int, error) {
	args := m.Called(chatName, userUUID)
	return args.Int(0), args.Error(1)
}

func (m *MockChatManager) GetChats(userUUID string) ([]database.Chat, error) {
	args := m.Called(userUUID)
	return args.Get(0).([]database.Chat), args.Error(1)
}

func (m *MockChatManager) CheckChat(userUUID string, chatID int) (bool, error) {
	args := m.Called(userUUID, chatID)
	return args.Bool(0), args.Error(1)
}

func (m *MockChatManager) RenameChat(chatID int, newName string) error {
	args := m.Called(chatID, newName)
	return args.Error(0)
}

func Test_ChatHandler(t *testing.T) {
	logger := logrus.New()
	testUUID := uuid.New()
	testTime := time.Now()

	tests := []struct {
		name           string
		method         string
		endpoint       string
		setupMocks     func(*MockChatManager)
		requestBody    string
		params         map[string]string
		expectedStatus int
		expectedBody   string
	}{
		// CreateHandler tests
		{
			name:     "Успешное создание чата",
			method:   "POST",
			endpoint: "/chats",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("CreateChat", "Test Chat", testUUID.String()).
					Return(123, nil)
			},
			requestBody:    `{"name":"Test Chat"}`,
			expectedStatus: http.StatusCreated,
			expectedBody:   `{"chat_id":123}`,
		},
		{
			name:     "Ошибка - невалидный JSON при создании",
			method:   "POST",
			endpoint: "/chats",
			setupMocks: func(mcm *MockChatManager) {
				// Мок не должен вызываться при ошибке парсинга JSON
			},
			requestBody:    `{"name": "invalid json`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"unexpected end of JSON input","error":"Invalid JSON format"}`,
		},
		{
			name:     "Ошибка - пользователь не найден при создании",
			method:   "POST",
			endpoint: "/chats",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("CreateChat", "Test Chat", testUUID.String()).
					Return(0, database.ErrUserNotFound)
			},
			requestBody:    `{"name":"Test Chat"}`,
			expectedStatus: http.StatusNotFound,
			expectedBody:   `{"details":"` + database.ErrUserNotFound.Error() + `","error":"User not found"}`,
		},
		{
			name:     "Ошибка базы данных при создании",
			method:   "POST",
			endpoint: "/chats",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("CreateChat", "Test Chat", testUUID.String()).
					Return(0, assert.AnError)
			},
			requestBody:    `{"name":"Test Chat"}`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"` + assert.AnError.Error() + `","error":"Error creating chat"}`,
		},

		// GetHandler tests
		{
			name:     "Успешное получение списка чатов",
			method:   "GET",
			endpoint: "/chats",
			setupMocks: func(mcm *MockChatManager) {
				chats := []database.Chat{
					{
						ChatID:     1,
						Name:       "Chat 1",
						CreateTime: testTime,
					},
					{
						ChatID:     2,
						Name:       "Chat 2",
						CreateTime: testTime,
					},
				}
				mcm.On("GetChats", testUUID.String()).
					Return(chats, nil)
			},
			expectedStatus: http.StatusOK,
			expectedBody:   `[{"chat_id":1,"name":"Chat 1","create_time":"` + testTime.Format(time.RFC3339Nano) + `"},{"chat_id":2,"name":"Chat 2","create_time":"` + testTime.Format(time.RFC3339Nano) + `"}]`,
		},
		{
			name:     "Успешное получение пустого списка чатов",
			method:   "GET",
			endpoint: "/chats",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("GetChats", testUUID.String()).
					Return([]database.Chat{}, nil)
			},
			expectedStatus: http.StatusOK,
			expectedBody:   `[]`,
		},
		{
			name:     "Ошибка базы данных при получении чатов",
			method:   "GET",
			endpoint: "/chats",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("GetChats", testUUID.String()).
					Return([]database.Chat{}, assert.AnError)
			},
			expectedStatus: http.StatusInternalServerError,
			expectedBody:   `{"details":"` + assert.AnError.Error() + `","error":"Failed to retrieve chats"}`,
		},

		// RenameHandler tests
		{
			name:     "Успешное переименование чата",
			method:   "PUT",
			endpoint: "/chats/123",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("RenameChat", 123, "New Chat Name").
					Return(nil)
			},
			requestBody:    `{"name":"New Chat Name"}`,
			params:         map[string]string{"chat_id": "123"},
			expectedStatus: http.StatusCreated,
			expectedBody:   `{"chat_id":123}`,
		},
		{
			name:     "Ошибка - невалидный ID чата при переименовании",
			method:   "PUT",
			endpoint: "/chats/invalid",
			setupMocks: func(mcm *MockChatManager) {
				// Мок не должен вызываться при невалидном ID
			},
			requestBody:    `{"name":"New Chat Name"}`,
			params:         map[string]string{"chat_id": "invalid"},
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Invalid chat ID format"}`,
		},
		{
			name:     "Ошибка - невалидный JSON при переименовании",
			method:   "PUT",
			endpoint: "/chats/123",
			setupMocks: func(mcm *MockChatManager) {
				// Мок не должен вызываться при ошибке парсинга JSON
			},
			requestBody:    `{"name": "invalid json`,
			params:         map[string]string{"chat_id": "123"},
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"unexpected end of JSON input","error":"Invalid JSON format"}`,
		},
		{
			name:     "Ошибка - пользователь не найден при переименовании",
			method:   "PUT",
			endpoint: "/chats/123",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("RenameChat", 123, "New Chat Name").
					Return(database.ErrUserNotFound)
			},
			requestBody:    `{"name":"New Chat Name"}`,
			params:         map[string]string{"chat_id": "123"},
			expectedStatus: http.StatusNotFound,
			expectedBody:   `{"details":"` + database.ErrUserNotFound.Error() + `","error":"User not found"}`,
		},
		{
			name:     "Ошибка базы данных при переименовании",
			method:   "PUT",
			endpoint: "/chats/123",
			setupMocks: func(mcm *MockChatManager) {
				mcm.On("RenameChat", 123, "New Chat Name").
					Return(assert.AnError)
			},
			requestBody:    `{"name":"New Chat Name"}`,
			params:         map[string]string{"chat_id": "123"},
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"` + assert.AnError.Error() + `","error":"Error creating chat"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание мока ChatManager
			chatManager := new(MockChatManager)

			// Настройка моков
			tt.setupMocks(chatManager)

			// Создание Fiber приложения и обработчика
			app := fiber.New()
			chatHandler := NewChat(chatManager, logger)

			// Добавляем middleware для установки UUID в контекст
			app.Use(func(c *fiber.Ctx) error {
				c.Locals("uuid", testUUID)
				return c.Next()
			})

			// Регистрируем маршруты
			app.Post("/chats", chatHandler.CreateHandler)
			app.Get("/chats", chatHandler.GetHandler)
			app.Put("/chats/:chat_id", chatHandler.RenameHandler)

			// Создание тестового запроса
			var req *http.Request
			if tt.requestBody != "" {
				req = httptest.NewRequest(tt.method, tt.endpoint, bytes.NewBufferString(tt.requestBody))
				req.Header.Set("Content-Type", "application/json")
			} else {
				req = httptest.NewRequest(tt.method, tt.endpoint, nil)
			}

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
			chatManager.AssertExpectations(t)
		})
	}
}
