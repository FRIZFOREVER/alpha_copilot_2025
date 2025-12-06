//nolint:errcheck
package handlers

import (
	"errors"
	"io"
	"jabki/internal/database"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockSearchManager мок для SearchManager интерфейса.
type MockSearchManager struct {
	mock.Mock
}

func (m *MockSearchManager) GetSearchedMessages(uuid string, searchQuery string) ([]database.Search, error) {
	args := m.Called(uuid, searchQuery)
	return args.Get(0).([]database.Search), args.Error(1)
}

func TestSearch_Handler(t *testing.T) {
	logger := logrus.New()

	// Создаем тестовые данные
	testUUID := uuid.New()
	testTime := time.Now()

	tests := []struct {
		name           string
		pattern        string
		setupMocks     func(*MockSearchManager)
		expectedStatus int
		expectedBody   string
	}{
		{
			name:    "Успешный поиск сообщений",
			pattern: "test query",
			setupMocks: func(msm *MockSearchManager) {
				messages := []database.Search{
					{
						QuestionID:      1,
						AnswerID:        1,
						Question:        "Test question?",
						QuestionTag:     stringPtr("general"),
						Answer:          "Test answer",
						QuestionTime:    testTime,
						AnswerTime:      testTime,
						VoiceURL:        "voice.mp3",
						QuestionFileURL: "question_file.pdf",
						AnswerFileURL:   "answer_file.pdf",
						Rating:          intPtr(5),
						ChatID:          100,
					},
					{
						QuestionID:      2,
						AnswerID:        2,
						Question:        "Another test?",
						QuestionTag:     nil,
						Answer:          "Another answer",
						QuestionTime:    testTime.Add(-time.Hour),
						AnswerTime:      testTime.Add(-30 * time.Minute),
						VoiceURL:        "",
						QuestionFileURL: "",
						AnswerFileURL:   "",
						Rating:          nil,
						ChatID:          101,
					},
				}
				msm.On("GetSearchedMessages", testUUID.String(), "test query").Return(messages, nil)
			},
			expectedStatus: http.StatusOK,
			expectedBody: `[{"question_id":1,"answer_id":1,"question":"Test question?","tag":"general","answer":"Test answer","question_time":"` + testTime.Format(time.RFC3339Nano) + `","answer_time":"` + testTime.Format(time.RFC3339Nano) + `","voice_url":"voice.mp3","question_file_url":"question_file.pdf","answer_file_url":"answer_file.pdf","rating":5,"chat_id":100},` +
				`{"question_id":2,"answer_id":2,"question":"Another test?","tag":null,"answer":"Another answer","question_time":"` + testTime.Add(-time.Hour).Format(time.RFC3339Nano) + `","answer_time":"` + testTime.Add(-30*time.Minute).Format(time.RFC3339Nano) + `","voice_url":"","question_file_url":"","answer_file_url":"","rating":null,"chat_id":101}]`,
		},
		{
			name:    "Пустой результат поиска",
			pattern: "nonexistent",
			setupMocks: func(msm *MockSearchManager) {
				msm.On("GetSearchedMessages", testUUID.String(), "nonexistent").Return([]database.Search{}, nil)
			},
			expectedStatus: http.StatusOK,
			expectedBody:   "[]",
		},
		{
			name:    "Ошибка базы данных",
			pattern: "error query",
			setupMocks: func(msm *MockSearchManager) {
				msm.On("GetSearchedMessages", testUUID.String(), "error query").Return([]database.Search{}, errors.New("database connection failed"))
			},
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Error in database","details":"database connection failed"}`,
		},
		{
			name:    "Пустой поисковый запрос",
			pattern: "",
			setupMocks: func(msm *MockSearchManager) {
				messages := []database.Search{
					{
						QuestionID:      3,
						AnswerID:        3,
						Question:        "Empty pattern search?",
						QuestionTag:     stringPtr("test"),
						Answer:          "Should work with empty pattern",
						QuestionTime:    testTime,
						AnswerTime:      testTime,
						VoiceURL:        "",
						QuestionFileURL: "",
						AnswerFileURL:   "",
						Rating:          intPtr(3),
						ChatID:          102,
					},
				}
				msm.On("GetSearchedMessages", testUUID.String(), "").Return(messages, nil)
			},
			expectedStatus: http.StatusOK,
			expectedBody:   `[{"question_id":3,"answer_id":3,"question":"Empty pattern search?","tag":"test","answer":"Should work with empty pattern","question_time":"` + testTime.Format(time.RFC3339Nano) + `","answer_time":"` + testTime.Format(time.RFC3339Nano) + `","voice_url":"","question_file_url":"","answer_file_url":"","rating":3,"chat_id":102}]`,
		},
		{
			name:    "Специальные символы в поисковом запросе",
			pattern: "test & query % _",
			setupMocks: func(msm *MockSearchManager) {
				msm.On("GetSearchedMessages", testUUID.String(), "test & query % _").Return([]database.Search{}, nil)
			},
			expectedStatus: http.StatusOK,
			expectedBody:   "[]",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создаем мок
			mockSearchManager := new(MockSearchManager)

			// Настраиваем мок
			tt.setupMocks(mockSearchManager)

			// Создаем Search хендлер
			search := NewSearch(mockSearchManager, logger)

			// Создаем Fiber приложение с middleware для установки UUID
			app := fiber.New()
			app.Use(func(c *fiber.Ctx) error {
				c.Locals("uuid", testUUID)
				return c.Next()
			})
			app.Get("/search", search.Handler)

			// Правильно создаем URL с параметрами
			params := url.Values{}
			if tt.pattern != "" {
				params.Add("pattern", tt.pattern)
			}

			urlPath := "/search"
			if len(params) > 0 {
				urlPath += "?" + params.Encode()
			}

			// Создаем запрос
			req := httptest.NewRequest(http.MethodGet, urlPath, nil)

			// Выполняем запрос
			resp, err := app.Test(req, -1)
			assert.NoError(t, err)
			defer resp.Body.Close()

			// Проверяем статус код
			assert.Equal(t, tt.expectedStatus, resp.StatusCode)

			// Проверяем тело ответа
			body, err := io.ReadAll(resp.Body)
			assert.NoError(t, err)
			assert.JSONEq(t, tt.expectedBody, string(body))

			// Проверяем вызовы моков
			mockSearchManager.AssertExpectations(t)
		})
	}
}

// Вспомогательные функции для создания указателей.
func stringPtr(s string) *string {
	return &s
}

func intPtr(i int) *int {
	return &i
}