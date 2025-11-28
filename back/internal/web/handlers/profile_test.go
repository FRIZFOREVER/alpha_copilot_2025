//nolint:thelper
package handlers

import (
	"bytes"
	"jabki/internal/database"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockProfileManager реализует интерфейс database.ProfileManager для тестов.
type MockProfileManager struct {
	mock.Mock
}

func (m *MockProfileManager) GetProfile(uuid string) (database.Profile, error) {
	args := m.Called(uuid)
	return args.Get(0).(database.Profile), args.Error(1)
}

func (m *MockProfileManager) UpdateOtherProfileInfo(uuid string, userInfo string, businessInfo string, additionalInstructions string) error {
	args := m.Called(uuid, userInfo, businessInfo, additionalInstructions)
	return args.Error(0)
}

func Test_ProfileHandler(t *testing.T) {
	logger := logrus.New()
	testUUID := uuid.New()

	// Вспомогательные переменные для указателей на строки
	userInfo := "test user info"
	businessInfo := "test business info"
	additionalInstructions := "test instructions"
	emptyString := ""

	tests := []struct {
		name           string
		method         string
		endpoint       string
		setupMocks     func(*MockProfileManager)
		requestBody    string
		expectedStatus int
		expectedBody   string
	}{
		// GetHandler tests
		{
			name:     "Успешное получение профиля",
			method:   "GET",
			endpoint: "/profile",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("GetProfile", testUUID.String()).
					Return(database.Profile{
						ID:                     1,
						Login:                  "testuser",
						FIO:                    "Test User",
						UserInfo:               &userInfo,
						BusinessInfo:           &businessInfo,
						AdditionalInstructions: &additionalInstructions,
					}, nil)
			},
			expectedStatus: http.StatusCreated,
			expectedBody:   `{"id":1,"login":"testuser","username":"Test User","user_info":"test user info","business_info":"test business info","additional_instructions":"test instructions"}`,
		},
		{
			name:     "Успешное получение профиля с nil полями",
			method:   "GET",
			endpoint: "/profile",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("GetProfile", testUUID.String()).
					Return(database.Profile{
						ID:                     1,
						Login:                  "testuser",
						FIO:                    "Test User",
						UserInfo:               nil,
						BusinessInfo:           nil,
						AdditionalInstructions: nil,
					}, nil)
			},
			expectedStatus: http.StatusCreated,
			expectedBody:   `{"id":1,"login":"testuser","username":"Test User","user_info":null,"business_info":null,"additional_instructions":null}`,
		},
		{
			name:     "Успешное получение профиля с пустыми строками",
			method:   "GET",
			endpoint: "/profile",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("GetProfile", testUUID.String()).
					Return(database.Profile{
						ID:                     1,
						Login:                  "testuser",
						FIO:                    "Test User",
						UserInfo:               &emptyString,
						BusinessInfo:           &emptyString,
						AdditionalInstructions: &emptyString,
					}, nil)
			},
			expectedStatus: http.StatusCreated,
			expectedBody:   `{"id":1,"login":"testuser","username":"Test User","user_info":"","business_info":"","additional_instructions":""}`,
		},
		{
			name:     "Ошибка - пользователь не найден при получении",
			method:   "GET",
			endpoint: "/profile",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("GetProfile", testUUID.String()).
					Return(database.Profile{}, database.ErrUserNotFound)
			},
			expectedStatus: http.StatusNotFound,
			expectedBody:   `{"error":"User not found","details":"` + database.ErrUserNotFound.Error() + `"}`,
		},
		{
			name:     "Ошибка базы данных при получении профиля",
			method:   "GET",
			endpoint: "/profile",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("GetProfile", testUUID.String()).
					Return(database.Profile{}, assert.AnError)
			},
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Error get user profile","details":"` + assert.AnError.Error() + `"}`,
		},

		// PutOtherInfoHandler tests
		{
			name:     "Успешное обновление дополнительной информации",
			method:   "PUT",
			endpoint: "/profile/other-info",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("UpdateOtherProfileInfo",
					testUUID.String(),
					"updated user info",
					"updated business info",
					"updated instructions",
				).Return(nil)
			},
			requestBody:    `{"user_info":"updated user info","business_info":"updated business info","additional_instructions":"updated instructions"}`,
			expectedStatus: http.StatusOK,
			expectedBody:   "",
		},
		{
			name:           "Ошибка - невалидный JSON при обновлении",
			method:         "PUT",
			endpoint:       "/profile/other-info",
			setupMocks:     func(mpm *MockProfileManager) {},
			requestBody:    `{"user_info": "invalid json`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Invalid JSON format","details":"unexpected end of JSON input"}`,
		},
		{
			name:     "Ошибка - пользователь не найден при обновлении",
			method:   "PUT",
			endpoint: "/profile/other-info",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("UpdateOtherProfileInfo",
					testUUID.String(),
					"test info",
					"test business",
					"test instructions",
				).Return(database.ErrUserNotFound)
			},
			requestBody:    `{"user_info":"test info","business_info":"test business","additional_instructions":"test instructions"}`,
			expectedStatus: http.StatusNotFound,
			expectedBody:   `{"error":"User not found","details":"` + database.ErrUserNotFound.Error() + `"}`,
		},
		{
			name:     "Ошибка базы данных при обновлении",
			method:   "PUT",
			endpoint: "/profile/other-info",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("UpdateOtherProfileInfo",
					testUUID.String(),
					"test info",
					"test business",
					"test instructions",
				).Return(assert.AnError)
			},
			requestBody:    `{"user_info":"test info","business_info":"test business","additional_instructions":"test instructions"}`,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Error get user profile","details":"` + assert.AnError.Error() + `"}`,
		},
		{
			name:     "Успешное обновление с пустыми полями",
			method:   "PUT",
			endpoint: "/profile/other-info",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("UpdateOtherProfileInfo",
					testUUID.String(),
					"",
					"",
					"",
				).Return(nil)
			},
			requestBody:    `{"user_info":"","business_info":"","additional_instructions":""}`,
			expectedStatus: http.StatusOK,
			expectedBody:   "",
		},
		{
			name:     "Успешное обновление с частичными данными",
			method:   "PUT",
			endpoint: "/profile/other-info",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("UpdateOtherProfileInfo",
					testUUID.String(),
					"only user info",
					"",
					"",
				).Return(nil)
			},
			requestBody:    `{"user_info":"only user info"}`,
			expectedStatus: http.StatusOK,
			expectedBody:   "",
		},
		{
			name:     "Успешное обновление когда некоторые поля null в JSON",
			method:   "PUT",
			endpoint: "/profile/other-info",
			setupMocks: func(mpm *MockProfileManager) {
				mpm.On("UpdateOtherProfileInfo",
					testUUID.String(),
					"user info",
					"",
					"",
				).Return(nil)
			},
			requestBody:    `{"user_info":"user info","business_info":null,"additional_instructions":null}`,
			expectedStatus: http.StatusOK,
			expectedBody:   "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание мока ProfileManager
			profileManager := new(MockProfileManager)

			// Настройка моков
			tt.setupMocks(profileManager)

			// Создание Fiber приложения и обработчика
			app := fiber.New()
			profileHandler := NewProfile(profileManager, logger)

			// Добавляем middleware для установки UUID в контекст
			app.Use(func(c *fiber.Ctx) error {
				c.Locals("uuid", testUUID)
				return c.Next()
			})

			// Регистрируем маршруты
			app.Get("/profile", profileHandler.GetHandler)
			app.Put("/profile/other-info", profileHandler.PutOtherInfoHandler)

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
			if tt.expectedBody != "" {
				assert.JSONEq(t, tt.expectedBody, body)
			} else {
				assert.Empty(t, body)
			}

			// Проверка вызовов моков
			profileManager.AssertExpectations(t)
		})
	}
}

// readBody вспомогательная функция для чтения тела ответа.
func readBody(t *testing.T, resp *http.Response) string {
	bodyBytes := make([]byte, resp.ContentLength)
	_, err := resp.Body.Read(bodyBytes)
	if err != nil && err.Error() != "EOF" {
		t.Fatalf("Failed to read response body: %v", err)
	}
	return string(bodyBytes)
}
