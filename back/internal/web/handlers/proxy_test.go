package handlers

import (
	"bytes"
	"errors"
	"io"
	"jabki/internal/s3"
	"jabki/internal/settings"
	"jabki/internal/web/middlewares"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gofiber/fiber/v2"
	minio "github.com/minio/minio-go"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// Мок-реализация minio.Object.
type mockMinioObject struct {
	reader io.ReadSeeker
	size   int64
}

func (m *mockMinioObject) Read(p []byte) (n int, err error) {
	return m.reader.Read(p)
}

func (m *mockMinioObject) Close() error {
	return nil
}

func (m *mockMinioObject) Stat() (minio.ObjectInfo, error) {
	return minio.ObjectInfo{
		Size: m.size,
	}, nil
}

type MockStorage struct {
	mock.Mock
}

// Get implements s3.AudioFileManager.
func (m *MockStorage) Get(bucket string, fileName string) (s3.File, error) {
	args := m.Called(bucket, fileName)
	return args.Get(0).(s3.File), args.Error(1)
}

// Upload implements s3.AudioFileManager.
func (m *MockStorage) Upload(bucketName string, uuid string, mp3Data []byte) (string, error) {
	args := m.Called(bucketName, uuid, mp3Data)
	return args.Get(0).(string), args.Error(1)
}

func Test_Webm_Proxy(t *testing.T) {
	logger := logrus.New()
	settings := settings.InitSettings(logger)
	tests := []struct {
		name             string
		audioFileName    string
		httpMethod       string
		setupMocks       func(*MockStorage)
		expectedStatus   int
		expectedResponse string
		body             []byte
	}{
		{
			name:          "Удачное проксирование файла",
			audioFileName: "someAudio_file.webm",
			httpMethod:    "GET",
			setupMocks: func(mps *MockStorage) {
				file := []byte("Мок файла")
				mockObject := &mockMinioObject{
					reader: bytes.NewReader(file),
					size:   int64(len(file)),
				}
				mps.On("Get", "voices", "someAudio_file.webm").Return(mockObject, nil)
			},
			expectedStatus:   http.StatusOK,
			expectedResponse: "Мок файла",
		},
		{
			name:          "Попытка получить неподдерживаемый формат файла",
			audioFileName: "someAudio_file.mp3",
			httpMethod:    "GET",
			setupMocks: func(mps *MockStorage) {
				file := []byte("Мок файла")
				mockObject := &mockMinioObject{
					reader: bytes.NewReader(file),
					size:   int64(len(file)),
				}
				mps.On("Get", "voices", "someAudio_file.mp3.webm").Return(mockObject, errors.New("123"))
			},
			expectedStatus:   http.StatusBadRequest,
			expectedResponse: `{"error":"123"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание моков.
			repo := new(MockStorage)

			// Настройка моков.
			tt.setupMocks(repo)

			// Создание сервиса и контроллера.

			app := fiber.New()

			authMiddleware := middlewares.NewUserAuthentication(settings.SecretUser, logger)
			app.Use(middlewares.Cors(settings.FrontOrigin), authMiddleware.Handler)
			audio := NewAudioProxy(repo, logger)
			app.Get("/voices/:file_name", audio.HandlerWebm)

			token, err := generateTokenForTest(settings.SecretUser)
			assert.NoError(t, err)

			// Готовим запрос.
			req := httptest.NewRequest(tt.httpMethod, "/voices/"+tt.audioFileName, bytes.NewReader(tt.body))
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

// MockFileManager реализует FileManager интерфейс для тестирования.
type MockFileManager struct {
	mock.Mock
}

// UploadFile загружает файл в объектное хранилище
// Возвращает путь к файлу или ошибку в случае неудачи.
func (m *MockFileManager) UploadFile(bucketName, uuid, fileExtension string, fileData []byte, contentType string) (string, error) {
	args := m.Called(bucketName, uuid, fileExtension, fileData, contentType)
	return args.String(0), args.Error(1)
}

// GetFile получает файл из объектного хранилища
// Возвращает объект файла или ошибку в случае неудачи.
func (m *MockFileManager) GetFile(bucket, fileName string) (s3.File, error) {
	args := m.Called(bucket, fileName)
	return args.Get(0).(s3.File), args.Error(1)
}

// ValidateFileSize проверяет размер файла перед загрузкой
// Возвращает ошибку если размер превышает допустимый или файл пустой.
func (m *MockFileManager) ValidateFileSize(fileData []byte) error {
	args := m.Called(fileData)
	return args.Error(0)
}

// GetMaxFileSize возвращает максимальный разрешенный размер файла.
func (m *MockFileManager) GetMaxFileSize() int64 {
	args := m.Called()
	return args.Get(0).(int64)
}

func Test_File_Proxy(t *testing.T) {
	logger := logrus.New()
	settings := settings.InitSettings(logger)
	tests := []struct {
		name             string
		audioFileName    string
		httpMethod       string
		setupMocks       func(*MockFileManager)
		expectedStatus   int
		expectedResponse string
		body             []byte
	}{
		{
			name:          "Удачное проксирование файла",
			audioFileName: "some_file.pdf",
			httpMethod:    "GET",
			setupMocks: func(mps *MockFileManager) {
				file := []byte("Мок файла")
				mockObject := &mockMinioObject{
					reader: bytes.NewReader(file),
					size:   int64(len(file)),
				}
				mps.On("GetFile", "files", "some_file.pdf").Return(mockObject, nil)
			},
			expectedStatus:   http.StatusOK,
			expectedResponse: "Мок файла",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание моков.
			repo := new(MockFileManager)

			// Настройка моков.
			tt.setupMocks(repo)

			// Создание сервиса и контроллера.

			app := fiber.New()

			authMiddleware := middlewares.NewUserAuthentication(settings.SecretUser, logger)
			app.Use(middlewares.Cors(settings.FrontOrigin), authMiddleware.Handler)
			proxy := NewFileProxy(repo, logger)
			app.Get("/files/:file_name", proxy.HandlerFile)

			token, err := generateTokenForTest(settings.SecretUser)
			assert.NoError(t, err)

			// Готовим запрос.
			req := httptest.NewRequest(tt.httpMethod, "/files/"+tt.audioFileName, bytes.NewReader(tt.body))
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
