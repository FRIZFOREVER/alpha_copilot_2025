package handlers

import (
	"jabki/internal/database"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockGraphLogRepository реализует интерфейс database.GraphLogRepository для тестов.
type MockGraphLogRepository struct {
	mock.Mock
}

func (m *MockGraphLogRepository) UpdateGraphLog(message string, tag string, answerID int) error {
	args := m.Called(message, tag, answerID)
	return args.Error(0)
}

func (m *MockGraphLogRepository) GetGraphLog(answerID int) ([]database.GraphLog, error) {
	args := m.Called(answerID)
	return args.Get(0).([]database.GraphLog), args.Error(1)
}

func Test_GraphLogHandler(t *testing.T) {
	logger := logrus.New()
	testTime := time.Now().UTC()

	tests := []struct {
		name           string
		setupMocks     func(*MockGraphLogRepository)
		queryParams    string
		expectedStatus int
		expectedBody   string
	}{
		{
			name: "Успешное получение логов графа",
			setupMocks: func(mglr *MockGraphLogRepository) {
				graphLogs := []database.GraphLog{
					{
						ID:      1,
						Tag:     "tag1",
						Message: "Message 1",
						TimeUTC: testTime,
					},
					{
						ID:      2,
						Tag:     "tag2",
						Message: "Message 2",
						TimeUTC: testTime,
					},
				}
				mglr.On("GetGraphLog", 123).
					Return(graphLogs, nil)
			},
			queryParams:    "answer_id=123",
			expectedStatus: http.StatusCreated,
			expectedBody:   `[{"id":1,"tag":"tag1","message":"Message 1","log_time":"` + testTime.Format(time.RFC3339Nano) + `"},{"id":2,"tag":"tag2","message":"Message 2","log_time":"` + testTime.Format(time.RFC3339Nano) + `"}]`,
		},
		{
			name: "Успешное получение пустого списка логов",
			setupMocks: func(mglr *MockGraphLogRepository) {
				mglr.On("GetGraphLog", 456).
					Return([]database.GraphLog{}, nil)
			},
			queryParams:    "answer_id=456",
			expectedStatus: http.StatusCreated,
			expectedBody:   `[]`,
		},
		{
			name: "Ошибка - отсутствует answer_id",
			setupMocks: func(mglr *MockGraphLogRepository) {
				// Мок не должен вызываться при отсутствии параметра
			},
			queryParams:    "",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"answer_id is a required query parameter"}`,
		},
		{
			name: "Ошибка - невалидный формат answer_id",
			setupMocks: func(mglr *MockGraphLogRepository) {
				// Мок не должен вызываться при невалидном ID
			},
			queryParams:    "answer_id=invalid",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Invalid answer ID format"}`,
		},
		{
			name: "Ошибка базы данных при получении логов",
			setupMocks: func(mglr *MockGraphLogRepository) {
				mglr.On("GetGraphLog", 789).
					Return([]database.GraphLog{}, assert.AnError)
			},
			queryParams:    "answer_id=789",
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"details":"` + assert.AnError.Error() + `","error":"Error get user profile"}`,
		},
		{
			name: "Успешное получение с одним логом",
			setupMocks: func(mglr *MockGraphLogRepository) {
				graphLogs := []database.GraphLog{
					{
						ID:      999,
						Tag:     "single_tag",
						Message: "Single message",
						TimeUTC: testTime,
					},
				}
				mglr.On("GetGraphLog", 999).
					Return(graphLogs, nil)
			},
			queryParams:    "answer_id=999",
			expectedStatus: http.StatusCreated,
			expectedBody:   `[{"id":999,"tag":"single_tag","message":"Single message","log_time":"` + testTime.Format(time.RFC3339Nano) + `"}]`,
		},
		{
			name: "Успешное получение с большим answer_id",
			setupMocks: func(mglr *MockGraphLogRepository) {
				mglr.On("GetGraphLog", 2147483647).
					Return([]database.GraphLog{}, nil)
			},
			queryParams:    "answer_id=2147483647",
			expectedStatus: http.StatusCreated,
			expectedBody:   `[]`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание мока GraphLogRepository
			graphLogRepo := new(MockGraphLogRepository)

			// Настройка моков
			tt.setupMocks(graphLogRepo)

			// Создание Fiber приложения и обработчика
			app := fiber.New()
			graphLogHandler := NewGraphLog(graphLogRepo, logger)

			// Регистрируем маршрут
			app.Get("/graph-log", graphLogHandler.Handler)

			// Создание тестового запроса
			url := "/graph-log"
			if tt.queryParams != "" {
				url += "?" + tt.queryParams
			}
			req := httptest.NewRequest(http.MethodGet, url, nil)

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
			graphLogRepo.AssertExpectations(t)
		})
	}
}
