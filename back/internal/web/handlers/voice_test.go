package handlers

import (
	"bytes"
	"io"
	"jabki/internal/client"
	"jabki/internal/settings"
	"jabki/internal/web/middlewares"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// AssamblyAIMock реализует интерфейс Recognizer через mock.Mock.
type AssamblyAIMock struct {
	mock.Mock
}

// MessageToRecognizer отправляет аудиоданные на распознавание и возвращает текст.
func (m *AssamblyAIMock) MessageToRecognizer(audioData []byte) (string, error) {
	args := m.Called(audioData)
	return args.String(0), args.Error(1)
}

// WhispererMock реализует интерфейс Whisperer через mock.Mock.
type WhispererMock struct {
	mock.Mock
}

// SendVoice отправляет голосовые данные и возвращает результат.
func (m *WhispererMock) SendVoice(voiceURL []byte) (*client.WhisperOut, error) {
	args := m.Called(voiceURL)

	// Получаем первый аргумент как *WhisperOut (может быть nil)
	var whisperOut *client.WhisperOut
	if args.Get(0) != nil {
		whisperOut = args.Get(0).(*client.WhisperOut)
	}

	return whisperOut, args.Error(1)
}

// createMultipartBody создает multipart/form-data тело с файлом.
func createMultipartBody(filename string, fileContent []byte) (*bytes.Buffer, string, error) {
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("voice", filename)
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

func Test_Voice(t *testing.T) {
	enable := true
	disable := false
	logger := logrus.New()
	settings := settings.InitSettings(logger)

	// Создаем тестовый аудиофайл
	testAudioContent := []byte("fake audio data")

	tests := []struct {
		name               string
		httpMethod         string
		isWhisperEnable    *bool
		isAssamblyAIEnable bool
		setupMocks         func(*MockStorage, *WhispererMock, *AssamblyAIMock)
		expectedStatus     int
		expectedResponse   string
		multipartBody      *bytes.Buffer
		contentType        string
	}{
		{
			name:               "Удачная запись голосового сообщения через Wisper",
			httpMethod:         "POST",
			isWhisperEnable:    &enable,
			isAssamblyAIEnable: disable,
			setupMocks: func(mps *MockStorage, wm *WhispererMock, aa *AssamblyAIMock) {
				mps.On("Upload", mock.Anything, mock.Anything, mock.Anything).Return("123", nil)
				wm.On("SendVoice", mock.Anything).Return(&client.WhisperOut{
					Message:  "123",
					VoiceURL: "/123.webm",
				}, nil)
			},
			expectedStatus:   http.StatusOK,
			expectedResponse: `{"question":"123","voice_url":"123"}`,
		},
		{
			name:               "Удачная запись голосового сообщения чере AssamblyAI",
			httpMethod:         "POST",
			isWhisperEnable:    &disable,
			isAssamblyAIEnable: enable,
			setupMocks: func(mps *MockStorage, wm *WhispererMock, aa *AssamblyAIMock) {
				mps.On("Upload", mock.Anything, mock.Anything, mock.Anything).Return("123.webm", nil)
				aa.On("MessageToRecognizer", mock.Anything).Return("123", nil)
			},
			expectedStatus:   http.StatusOK,
			expectedResponse: `{"question":"123","voice_url":"123.webm"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Создание моков
			storage := new(MockStorage)
			whisper := new(WhispererMock)
			assamblyAI := new(AssamblyAIMock)

			// Настройка моков
			tt.setupMocks(storage, whisper, assamblyAI)

			// Создание сервиса и контроллера
			app := fiber.New()

			authMiddleware := middlewares.NewUserAuthentication(settings.SecretUser, logger)
			app.Use(middlewares.Cors(settings.FrontOrigin), authMiddleware.Handler)
			voice := NewVoice(assamblyAI, whisper, storage, tt.isWhisperEnable, tt.isAssamblyAIEnable, logger)
			app.Post("/voice", voice.Handler)

			token, err := generateTokenForTest(settings.SecretUser)
			assert.NoError(t, err)

			// Готовим запрос
			var req *http.Request

			if tt.multipartBody != nil {
				// Если указано multipart тело, используем его
				req = httptest.NewRequest(tt.httpMethod, "/voice", tt.multipartBody)
				if tt.contentType != "" {
					req.Header.Set("Content-Type", tt.contentType)
				}
			} else {
				// Для первого теста создаем правильный multipart запрос с файлом
				body, contentType, err := createMultipartBody("test_voice.webm", testAudioContent)
				assert.NoError(t, err)

				req = httptest.NewRequest(tt.httpMethod, "/voice", body)
				req.Header.Set("Content-Type", contentType)
			}

			req.Header.Set("Authorization", "Bearer "+token)

			// Выполняем тестовый запрос
			resp, err := app.Test(req, -1)
			if err != nil {
				t.Fatalf("Failed to test request: %v", err)
			}
			defer func() {
				assert.NoError(t, resp.Body.Close())
			}()

			// Проверяем статус ответа
			assert.Equal(t, tt.expectedStatus, resp.StatusCode)

			// Читаем тело ответа
			body, err := io.ReadAll(resp.Body)
			assert.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, resp.StatusCode)
			assert.Equal(t, tt.expectedResponse, string(body))

			// Проверка, что все ожидаемые вызовы были выполнены
			storage.AssertExpectations(t)
		})
	}
}
