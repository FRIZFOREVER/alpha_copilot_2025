package handlers

import (
	"bytes"
	"io"
	"jabki/internal/database"
	"jabki/internal/settings"
	"jabki/internal/web/middlewares"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// type HistoryManager interface {
// 	GetHistory(chatID int, uuid string, historyLen int, tag string) ([]Message, error)
// 	HideMessages(chatID int) error
// 	CheckChat(userUUID string, chatID int) (bool, error)
// }

type MockHistoryRepository struct {
	mock.Mock
}

func (m *MockHistoryRepository) CheckChat(userUUID string, chatID int) (bool, error) {
	args := m.Called(userUUID, chatID)
	return args.Get(0).(bool), args.Error(1)
}

func (m *MockHistoryRepository) GetHistory(chatID int, uuid string, historyLen int, tag string) ([]database.Message, error) {
	args := m.Called(chatID, uuid, historyLen, tag)
	return args.Get(0).([]database.Message), args.Error(1)
}

func (m *MockHistoryRepository) HideMessages(chatID int) error {
	args := m.Called(chatID)
	return args.Error(0)
}

func Test_History(t *testing.T) {
	logger := logrus.New()
	settings := settings.InitSettings(logger)
	tests := []struct {
		name             string
		chatID           string
		httpMethod       string
		body             []byte
		setupMocks       func(*MockHistoryRepository)
		expectedStatus   int
		expectedResponse string
	}{
		{
			name:       "1) Запрос на получение пустой истории",
			chatID:     "1",
			httpMethod: fiber.MethodGet,
			body:       []byte(`{"answer_id": 2,"rating": 5}`),
			setupMocks: func(mr *MockHistoryRepository) {
				mr.On("CheckChat", "00000000-0000-0000-0000-000000000000", 1).Return(true, nil)
				mr.On("GetHistory", 1, "00000000-0000-0000-0000-000000000000", mock.Anything, mock.Anything).Return([]database.Message{}, nil)
			},
			expectedStatus:   fiber.StatusOK,
			expectedResponse: "[]",
		},
		{
			name:       "2) Запрос на получение пустой запполненной истории",
			chatID:     "1",
			httpMethod: fiber.MethodGet,
			body:       []byte(`{"answer_id": 2,"rating": 5}`),
			setupMocks: func(mr *MockHistoryRepository) {
				stringPtr := "programming"
				intPtr := 5
				mr.On("CheckChat", "00000000-0000-0000-0000-000000000000", 1).Return(true, nil)
				mr.On("GetHistory", 1, "00000000-0000-0000-0000-000000000000", mock.Anything, mock.Anything).Return([]database.Message{
					// Элемент 1
					{
						QuestionID:      1001,
						AnswerID:        2001,
						Question:        "Какие основные преимущества использования Go?",
						QuestionTag:     &stringPtr,
						Answer:          "Go предлагает простой синтаксис, эффективную сборку мусора, встроенную поддержку конкурентности через горутины и каналы, а также отличную производительность.",
						QuestionTime:    time.Date(2024, 1, 15, 10, 30, 0, 0, time.UTC),
						AnswerTime:      time.Date(2024, 1, 15, 10, 35, 0, 0, time.UTC),
						VoiceURL:        "https://example.com/voices/answer2001.mp3",
						QuestionFileURL: "https://example.com/files/go_benefits.pdf",
						Rating:          &intPtr,
					},

					// Элемент 2
					{
						QuestionID:      1002,
						AnswerID:        2002,
						Question:        "Как работает сборка мусора в Go?",
						QuestionTag:     &stringPtr,
						Answer:          "В Go используется параллельная трехцветная маркировка и очистка с минимальными паузами, что позволяет эффективно управлять памятью без значительного влияния на производительность.",
						QuestionTime:    time.Date(2024, 1, 16, 14, 20, 0, 0, time.UTC),
						AnswerTime:      time.Date(2024, 1, 16, 14, 25, 0, 0, time.UTC),
						VoiceURL:        "",
						QuestionFileURL: "https://example.com/files/gc_explanation.pdf",
						Rating:          &intPtr,
					},

					// Элемент 3
					{
						QuestionID:      1003,
						AnswerID:        2003,
						Question:        "Что такое горутины и чем они отличаются от потоков?",
						QuestionTag:     nil,
						Answer:          "Горутины - это легковесные потоки, управляемые средой выполнения Go. Они потребляют меньше памяти чем системные потоки и создаются/уничтожаются быстрее. Горутины планируются средой выполнения Go, а не операционной системой.",
						QuestionTime:    time.Date(2024, 1, 17, 9, 15, 0, 0, time.UTC),
						AnswerTime:      time.Date(2024, 1, 17, 9, 18, 0, 0, time.UTC),
						VoiceURL:        "https://example.com/voices/goroutines.mp3",
						QuestionFileURL: "",
						Rating:          nil,
					},
				}, nil)
			},
			expectedStatus:   fiber.StatusOK,
			expectedResponse: `[{"question_id":1001,"answer_id":2001,"question":"Какие основные преимущества использования Go?","tag":"programming","answer":"Go предлагает простой синтаксис, эффективную сборку мусора, встроенную поддержку конкурентности через горутины и каналы, а также отличную производительность.","question_time":"2024-01-15T10:30:00Z","answer_time":"2024-01-15T10:35:00Z","voice_url":"https://example.com/voices/answer2001.mp3","question_file_url":"https://example.com/files/go_benefits.pdf","rating":5,"answer_file_url":null},{"question_id":1002,"answer_id":2002,"question":"Как работает сборка мусора в Go?","tag":"programming","answer":"В Go используется параллельная трехцветная маркировка и очистка с минимальными паузами, что позволяет эффективно управлять памятью без значительного влияния на производительность.","question_time":"2024-01-16T14:20:00Z","answer_time":"2024-01-16T14:25:00Z","voice_url":"","question_file_url":"https://example.com/files/gc_explanation.pdf","rating":5,"answer_file_url":null},{"question_id":1003,"answer_id":2003,"question":"Что такое горутины и чем они отличаются от потоков?","tag":null,"answer":"Горутины - это легковесные потоки, управляемые средой выполнения Go. Они потребляют меньше памяти чем системные потоки и создаются/уничтожаются быстрее. Горутины планируются средой выполнения Go, а не операционной системой.","question_time":"2024-01-17T09:15:00Z","answer_time":"2024-01-17T09:18:00Z","voice_url":"https://example.com/voices/goroutines.mp3","question_file_url":"","rating":null,"answer_file_url":null}]`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание моков.
			repo := new(MockHistoryRepository)

			// Настройка моков.
			tt.setupMocks(repo)

			// Создание сервиса и контроллера.

			app := fiber.New()

			authMiddleware := middlewares.NewUserAuthentication(settings.SecretUser, logger)
			app.Use(middlewares.Cors(settings.FrontOrigin), authMiddleware.Handler)
			history := NewHistory(repo, logger)
			app.Get("/history/:chat_id", history.Handler)

			token, err := generateTokenForTest(settings.SecretUser)
			assert.NoError(t, err)

			// Готовим запрос.
			req := httptest.NewRequest(tt.httpMethod, "/history/"+tt.chatID, bytes.NewReader(tt.body))
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
