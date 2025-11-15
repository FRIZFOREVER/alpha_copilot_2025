package handlers

import (
	"bytes"
	"io"
	"jabki/internal/client"
	"jabki/internal/database"
	"jabki/internal/settings"
	"jabki/internal/web/middlewares"
	"net/http/httptest"
	"regexp"
	"testing"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockStreamClient struct {
	mock.Mock
}

// StreamRequestToModelWithTimeout implements client.StreamMessageProcessor.
func (m *MockStreamClient) StreamRequestToModelWithTimeout(payload client.PayloadStream, timeout time.Duration) (<-chan *client.StreamMessage, string, error) {
	panic("unimplemented")
}

func (m *MockStreamClient) StreamRequestToModel(payload client.PayloadStream) (<-chan *client.StreamMessage, string, error) {
	args := m.Called(payload)
	return args.Get(0).(<-chan *client.StreamMessage), args.Get(1).(string), args.Error(2)
}

// // StreamMessageProcessor интерфейс для работы с потоковыми сообщениями.
// type StreamMessageProcessor interface {
// 	// StreamRequestToModel выполняет запрос и возвращает канал для чтения сообщений StreamMessage
// 	// Возвращает канал сообщений, тег из заголовков ответа и ошибку
// 	StreamRequestToModel(payload PayloadStream) (<-chan *StreamMessage, string, error)

// 	// StreamRequestToModelWithTimeout выполняет запрос с таймаутом
// 	// Возвращает канал сообщений, тег из заголовков ответа и ошибку
// 	StreamRequestToModelWithTimeout(payload PayloadStream, timeout time.Duration) (<-chan *StreamMessage, string, error)
// }

type MockMessageManager struct {
	mock.Mock
}

// WriteMessage implements MessageManager.
func (m *MockMessageManager) WriteMessage(chatID int, question, answer string, questionTime, answerTime time.Time, tag string, voiceURL string, fileURL string) (questionID int, answerID int, err error) {
	args := m.Called(chatID, question, answer, questionTime, answerTime, tag, voiceURL, fileURL)
	return args.Int(0), args.Int(1), args.Error(2)
}

// UpdateAnswer implements MessageManager.
func (m *MockMessageManager) UpdateAnswer(answerID int, answer string) (int64, error) {
	args := m.Called(answerID, answer)
	return args.Get(0).(int64), args.Error(1)
}

// UpdateAnswerAndQuestionTag implements MessageManager.
func (m *MockMessageManager) UpdateAnswerAndQuestionTag(answerID, questionID int, answer string, tag string) (int64, error) {
	args := m.Called(answerID, questionID, answer, tag)
	return args.Get(0).(int64), args.Error(1)
}

// WriteEmptyMessage implements MessageManager.
func (m *MockMessageManager) WriteEmptyMessage(chatID int, questionTime, answerTime time.Time, voiceURL string) (questionID int, answerID int, err error) {
	args := m.Called(chatID, questionTime, answerTime, voiceURL)
	return args.Int(0), args.Int(1), args.Error(2)
}

// CheckChat implements MessageManager.
func (m *MockMessageManager) CheckChat(userUUID string, chatID int) (bool, error) {
	args := m.Called(userUUID, chatID)
	return args.Bool(0), args.Error(1)
}

// GetHistory implements MessageManager.
func (m *MockMessageManager) GetHistory(chatID int, uuid string, historyLen int, tag string) ([]database.Message, error) {
	args := m.Called(chatID, uuid, historyLen, tag)
	return args.Get(0).([]database.Message), args.Error(1)
}

// // MessageManager - единый интерфейс для управления сообщениями.
// type MessageManager interface {
// 	WriteMessage(
// 		chatID int,
// 		question, answer string,
// 		questionTime, answerTime time.Time,
// 		tag string,
// 		voiceURL string,
// 		fileURL string,
// 	) (questionID int, answerID int, err error)
// 	UpdateAnswer(answerID int, answer string) (int64, error)
// 	UpdateAnswerAndQuestionTag(answerID, questionID int, answer string, tag string) (int64, error)
// 	WriteEmptyMessage(chatID int, questionTime, answerTime time.Time, voiceURL string) (questionID int, answerID int, err error)
// 	CheckChat(userUUID string, chatID int) (bool, error)
// 	GetHistory(chatID int, uuid string, historyLen int, tag string) ([]Message, error)
// }

func Test_Stream(t *testing.T) {
	logger := logrus.New()
	settings := settings.InitSettings(logger)
	tests := []struct {
		name             string
		chatID           string
		httpMethod       string
		body             []byte
		setupMocks       func(*MockMessageManager, *MockStreamClient)
		expectedStatus   int
		expectedResponse string
	}{
		{
			name:       "1) Тест стриминга сообщений",
			chatID:     "1",
			httpMethod: fiber.MethodPost,
			body:       []byte(`{"question":"Тестовый вопрос","voice_url":"","file_url":"","tag":"test-tag","mode":"stream"}`),
			setupMocks: func(mr *MockMessageManager, mc *MockStreamClient) {
				// Создаем канал для стримовых сообщений
				streamChan := make(chan *client.StreamMessage)

				// Запускаем горутину для заполнения канала тестовыми данными
				go func() {
					defer close(streamChan)

					// Первое сообщение - начало ответа
					streamChan <- &client.StreamMessage{
						Model:     "test-model",
						CreatedAt: time.Now().Format(time.RFC3339),
						Done:      false,
						Message: client.MessageContent{
							Role:    "assistant",
							Content: "Это тестовый ответ",
						},
					}

					// Второе сообщение - продолжение ответа
					streamChan <- &client.StreamMessage{
						Model:     "test-model",
						CreatedAt: time.Now().Format(time.RFC3339),
						Done:      false,
						Message: client.MessageContent{
							Role:    "assistant",
							Content: " на ваш вопрос",
						},
					}

					// Финальное сообщение - завершение стрима
					streamChan <- &client.StreamMessage{
						Model:         "test-model",
						CreatedAt:     time.Now().Format(time.RFC3339),
						Done:          true,
						DoneReason:    "stop",
						TotalDuration: int64Ptr(1000),
						Message: client.MessageContent{
							Role:    "assistant",
							Content: "Это тестовый ответ на ваш вопрос",
						},
					}
				}()

				// Теперь используем созданный канал в моке - преобразуем в канал только для чтения
				mr.On("CheckChat", "00000000-0000-0000-0000-000000000000", 1).Return(true, nil)
				mr.On("GetHistory", 1, "00000000-0000-0000-0000-000000000000", mock.Anything, mock.Anything).Return([]database.Message{}, nil)
				mr.On("WriteMessage",
					mock.AnythingOfType("int"),       // chatID
					"Тестовый вопрос",                // question
					"",                               // answer
					mock.AnythingOfType("time.Time"), // questionTime
					mock.AnythingOfType("time.Time"), // answerTime
					"test-tag",                       // tag
					"",                               // voiceURL
					"",                               // fileURL
				).Return(123, 456, nil) // questionID, answerID, error
				mc.On("StreamRequestToModel", mock.AnythingOfType("client.PayloadStream")).Return((<-chan *client.StreamMessage)(streamChan), "test-tag", nil)
				mr.On("UpdateAnswer", mock.Anything, mock.Anything).Return(int64(0), nil)
			},
			expectedStatus:   fiber.StatusOK,
			expectedResponse: "data: {\"question_id\":123,\"answer_id\":456,\"question_time\":\"2025-11-15T15:03:46.6536418Z\",\"tag\":\"test-tag\"}\n\ndata: {\"content\":\"Это тестовый ответ\",\"time\":\"2025-11-15T15:03:46.6548335Z\",\"done\":false}\n\ndata: {\"content\":\" на ваш вопрос\",\"time\":\"2025-11-15T15:03:46.6548335Z\",\"done\":false}\n\ndata: {\"content\":\"Это тестовый ответ на ваш вопрос\",\"time\":\"2025-11-15T15:03:46.6548335Z\",\"done\":false}\n\ndata: {\"content\":\"\",\"time\":\"2025-11-15T15:03:46.6548335Z\",\"done\":true}\n\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание моков.
			repo := new(MockMessageManager)
			client := new(MockStreamClient)
			// Настройка моков.
			tt.setupMocks(repo, client)

			// Создание сервиса и контроллера.

			app := fiber.New()

			authMiddleware := middlewares.NewUserAuthentication(settings.SecretUser, logger)
			app.Use(middlewares.Cors(settings.FrontOrigin), authMiddleware.Handler)
			stream := NewStream(client, repo, 5, logger)
			app.Post("/message_stream/:chat_id", stream.Handler)

			token, err := generateTokenForTest(settings.SecretUser)
			assert.NoError(t, err)

			// Готовим запрос.
			req := httptest.NewRequest(tt.httpMethod, "/message_stream/"+tt.chatID, bytes.NewReader(tt.body))
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
			assert.Equal(t, replaceTimeWithMockRegex(tt.expectedResponse), replaceTimeWithMockRegex(string(body)))

			// Проверка, что все ожидаемые вызовы были выполнены.

			repo.AssertExpectations(t)
		})
	}
}

// Вспомогательная функция для создания указателей на int64.
func int64Ptr(i int64) *int64 {
	return &i
}

func replaceTimeWithMockRegex(input string) string {
	// Регулярное выражение для поиска временных меток в формате ISO 8601
	timeRegex := regexp.MustCompile(`\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z`)

	// Заменяем все временные метки на фиксированное мок-значение
	return timeRegex.ReplaceAllString(input, "2024-01-01T12:00:00.0000000Z")
}
