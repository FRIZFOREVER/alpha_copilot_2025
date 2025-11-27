//nolint:thelper
package handlers

import (
	"bytes"
	"io"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
)

// createMultipartFileBody создает multipart/form-data тело с файлом.
func createMultipartFileBody(filename string, fileContent []byte, fieldName string) (*bytes.Buffer, string, error) {
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile(fieldName, filename)
	if err != nil {
		return nil, "", err
	}

	_, err = part.Write(fileContent)
	if err != nil {
		return nil, "", err
	}

	err = writer.Close()
	if err != nil {
		return nil, "", err
	}

	return body, writer.FormDataContentType(), nil
}

func Test_FileHandler(t *testing.T) {
	logger := logrus.New()

	// Тестовые данные
	testFileContent := []byte("test file content")
	testUUID := uuid.New()
	testFileURL := "https://storage.example.com/files/" + testUUID.String() + ".txt"

	tests := []struct {
		name           string
		setupMocks     func(*MockFileManager)
		setupRequest   func() *http.Request
		expectedStatus int
		expectedBody   string
	}{
		{
			name: "Успешная загрузка файла",
			setupMocks: func(mfm *MockFileManager) {
				// Мок не вызывает ValidateFileSize, так как он не используется в обработчике
				mfm.On("UploadFile", "files", testUUID.String(), ".txt", testFileContent, "application/octet-stream").
					Return(testFileURL, nil)
			},
			setupRequest: func() *http.Request {
				body, contentType, err := createMultipartFileBody("test.txt", testFileContent, "file")
				assert.NoError(t, err)

				req := httptest.NewRequest(http.MethodPost, "/file", body)
				req.Header.Set("Content-Type", contentType)
				return req
			},
			expectedStatus: http.StatusOK,
			expectedBody:   `{"file_url":"` + testFileURL + `"}`,
		},
		{
			name: "Ошибка - файл не передан",
			setupMocks: func(mfm *MockFileManager) {
				// Моки не должны вызываться при отсутствии файла
			},
			setupRequest: func() *http.Request {
				req := httptest.NewRequest(http.MethodPost, "/file", nil)
				req.Header.Set("Content-Type", "multipart/form-data")
				return req
			},
			expectedStatus: http.StatusBadRequest,
			expectedBody:   `{"error":"Не удалось получить файл: request Content-Type has bad boundary or is not multipart/form-data"}`,
		},
		{
			name: "Ошибка загрузки в S3",
			setupMocks: func(mfm *MockFileManager) {
				mfm.On("UploadFile", "files", testUUID.String(), ".txt", testFileContent, "application/octet-stream").
					Return("", assert.AnError)
			},
			setupRequest: func() *http.Request {
				body, contentType, err := createMultipartFileBody("test.txt", testFileContent, "file")
				assert.NoError(t, err)

				req := httptest.NewRequest(http.MethodPost, "/file", body)
				req.Header.Set("Content-Type", contentType)
				return req
			},
			expectedStatus: http.StatusInternalServerError,
			expectedBody:   `{"details":"assert.AnError general error for testing","error":"Не удалось загрузить файл в хранилище"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание мока FileManager
			fileManager := new(MockFileManager)

			// Настройка моков
			tt.setupMocks(fileManager)

			// Создание Fiber приложения и обработчика
			app := fiber.New()
			fileHandler := NewFile(fileManager, logger)

			// Добавляем middleware для установки UUID в контекст
			app.Use(func(c *fiber.Ctx) error {
				c.Locals("uuid", testUUID)
				return c.Next()
			})

			app.Post("/file", fileHandler.Handler)

			// Создание тестового запроса
			req := tt.setupRequest()

			// Выполнение запроса
			resp, err := app.Test(req, -1)
			assert.NoError(t, err)
			defer func() {
				assert.NoError(t, resp.Body.Close())
			}()

			// Проверка статуса ответа
			assert.Equal(t, tt.expectedStatus, resp.StatusCode)

			// Чтение и проверка тела ответа
			body, err := io.ReadAll(resp.Body)
			assert.NoError(t, err)
			assert.Equal(t, tt.expectedBody, string(body))

			// Проверка вызовов моков
			fileManager.AssertExpectations(t)
		})
	}
}

func Test_FileHandler_ErrorScenarios(t *testing.T) {
	logger := logrus.New()
	testUUID := uuid.New()
	testFileContent := []byte("test file content")

	tests := []struct {
		name           string
		setupRequest   func() *http.Request
		expectedStatus int
		checkBody      func(t *testing.T, body string)
	}{
		{
			name: "Ошибка - неправильное поле формы",
			setupRequest: func() *http.Request {
				// Используем неправильное имя поля (не "file")
				body, contentType, err := createMultipartFileBody("test.txt", testFileContent, "wrong_field")
				assert.NoError(t, err)

				req := httptest.NewRequest(http.MethodPost, "/file", body)
				req.Header.Set("Content-Type", contentType)
				return req
			},
			expectedStatus: http.StatusBadRequest,
			checkBody: func(t *testing.T, body string) {
				assert.Contains(t, body, `{"error":"Не удалось получить файл:`)
			},
		},
		{
			name: "Ошибка - не multipart запрос",
			setupRequest: func() *http.Request {
				req := httptest.NewRequest(http.MethodPost, "/file", bytes.NewBufferString("plain text"))
				req.Header.Set("Content-Type", "text/plain")
				return req
			},
			expectedStatus: http.StatusBadRequest,
			checkBody: func(t *testing.T, body string) {
				assert.Contains(t, body, `{"error":"Не удалось получить файл:`)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fileManager := new(MockFileManager)
			fileHandler := NewFile(fileManager, logger)

			app := fiber.New()
			app.Use(func(c *fiber.Ctx) error {
				c.Locals("uuid", testUUID)
				return c.Next()
			})
			app.Post("/file", fileHandler.Handler)

			req := tt.setupRequest()
			resp, err := app.Test(req, -1)
			assert.NoError(t, err)
			defer func() {
				assert.NoError(t, resp.Body.Close())
			}()

			assert.Equal(t, tt.expectedStatus, resp.StatusCode)

			body, err := io.ReadAll(resp.Body)
			assert.NoError(t, err)

			tt.checkBody(t, string(body))
		})
	}
}
