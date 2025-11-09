package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type RecognizerClient struct {
	baseURL string
	path    string
	apiKey  string
	client  *http.Client
}

func NewRecognizerClient(baseURL, path, apiKey string) *RecognizerClient {
	return &RecognizerClient{
		baseURL: baseURL,
		path:    path,
		apiKey:  apiKey,
		client:  &http.Client{},
	}
}

type UploadResponse struct {
	UploadURL string `json:"upload_url"`
}

type TranscriptRequest struct {
	AudioURL    string `json:"audio_url"`
	LanguageCode string `json:"language_code"`
}

type TranscriptResponse struct {
	ID string `json:"id"`
}

type TranscriptStatusResponse struct {
	Status string `json:"status"`
	Text   string `json:"text"`
	Error  string `json:"error"`
}

func (c *RecognizerClient) MessageToRecognizer(audioData []byte) (string, error) {
	// 1. Загрузка аудио файла
	uploadURL, err := c.uploadAudio(audioData)
	if err != nil {
		return "", fmt.Errorf("ошибка загрузки аудио: %w", err)
	}

	// 2. Запрос транскрипции
	transcriptID, err := c.requestTranscript(uploadURL)
	if err != nil {
		return "", fmt.Errorf("ошибка запроса транскрипции: %w", err)
	}

	// 3. Ожидание завершения транскрипции
	transcript, err := c.waitForTranscript(transcriptID)
	if err != nil {
		return "", fmt.Errorf("ошибка ожидания транскрипции: %w", err)
	}

	return transcript, nil
}

func (c *RecognizerClient) uploadAudio(audioData []byte) (string, error) {
	// Валидация API ключа
	if strings.TrimSpace(c.apiKey) == "" {
		return "", fmt.Errorf("API ключ AssemblyAI не установлен (ASSEMBLYAI_API_KEY пустой)")
	}

	fullURL := c.baseURL + c.path + "/upload"
	
	req, err := http.NewRequest("POST", fullURL, bytes.NewBuffer(audioData))
	if err != nil {
		return "", fmt.Errorf("ошибка создания запроса: %w", err)
	}

	// AssemblyAI требует просто значение API ключа в заголовке Authorization (без "Bearer")
	apiKey := strings.TrimSpace(c.apiKey)
	req.Header.Set("Authorization", apiKey)
	req.Header.Set("Content-Type", "application/octet-stream")

	resp, err := c.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("ошибка выполнения запроса: %w", err)
	}
	defer resp.Body.Close()

	// Читаем тело ответа для диагностики ошибок
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("ошибка чтения ответа: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		errorMsg := fmt.Sprintf("ошибка загрузки: статус %d", resp.StatusCode)
		// Пытаемся извлечь сообщение об ошибке из ответа
		if len(body) > 0 {
			var errorResp struct {
				Error string `json:"error"`
			}
			if err := json.Unmarshal(body, &errorResp); err == nil && errorResp.Error != "" {
				errorMsg += ": " + errorResp.Error
			} else {
				errorMsg += ": " + string(body)
			}
		}
		return "", fmt.Errorf(errorMsg)
	}

	var uploadResp UploadResponse
	if err := json.Unmarshal(body, &uploadResp); err != nil {
		return "", fmt.Errorf("ошибка парсинга ответа: %w", err)
	}

	return uploadResp.UploadURL, nil
}

func (c *RecognizerClient) requestTranscript(uploadURL string) (string, error) {
	// Валидация API ключа
	if strings.TrimSpace(c.apiKey) == "" {
		return "", fmt.Errorf("API ключ AssemblyAI не установлен (ASSEMBLYAI_API_KEY пустой)")
	}

	fullURL := c.baseURL + c.path + "/transcript"
	
	transcriptReq := TranscriptRequest{
		AudioURL:     uploadURL,
		LanguageCode: "ru",
	}

	jsonData, err := json.Marshal(transcriptReq)
	if err != nil {
		return "", fmt.Errorf("ошибка маршалинга запроса: %w", err)
	}

	req, err := http.NewRequest("POST", fullURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("ошибка создания запроса: %w", err)
	}

	apiKey := strings.TrimSpace(c.apiKey)
	req.Header.Set("Authorization", apiKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("ошибка выполнения запроса: %w", err)
	}
	defer resp.Body.Close()

	// Читаем тело ответа для диагностики ошибок
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("ошибка чтения ответа: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		errorMsg := fmt.Sprintf("ошибка запроса транскрипции: статус %d", resp.StatusCode)
		if len(body) > 0 {
			var errorResp struct {
				Error string `json:"error"`
			}
			if err := json.Unmarshal(body, &errorResp); err == nil && errorResp.Error != "" {
				errorMsg += ": " + errorResp.Error
			} else {
				errorMsg += ": " + string(body)
			}
		}
		return "", fmt.Errorf(errorMsg)
	}

	var transcriptResp TranscriptResponse
	if err := json.Unmarshal(body, &transcriptResp); err != nil {
		return "", fmt.Errorf("ошибка парсинга ответа: %w", err)
	}

	return transcriptResp.ID, nil
}

func (c *RecognizerClient) waitForTranscript(transcriptID string) (string, error) {
	// Валидация API ключа
	if strings.TrimSpace(c.apiKey) == "" {
		return "", fmt.Errorf("API ключ AssemblyAI не установлен (ASSEMBLYAI_API_KEY пустой)")
	}

	fullURL := c.baseURL + c.path + "/transcript/" + transcriptID
	
	maxAttempts := 30
	attempts := 0

	for attempts < maxAttempts {
		time.Sleep(1 * time.Second)

		req, err := http.NewRequest("GET", fullURL, nil)
		if err != nil {
			return "", fmt.Errorf("ошибка создания запроса: %w", err)
		}

		apiKey := strings.TrimSpace(c.apiKey)
		req.Header.Set("Authorization", apiKey)

		resp, err := c.client.Do(req)
		if err != nil {
			return "", fmt.Errorf("ошибка выполнения запроса: %w", err)
		}

		body, err := io.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			return "", fmt.Errorf("ошибка чтения ответа: %w", err)
		}

		if resp.StatusCode != http.StatusOK {
			errorMsg := fmt.Sprintf("ошибка проверки статуса транскрипции: статус %d", resp.StatusCode)
			if len(body) > 0 {
				var errorResp struct {
					Error string `json:"error"`
				}
				if err := json.Unmarshal(body, &errorResp); err == nil && errorResp.Error != "" {
					errorMsg += ": " + errorResp.Error
				} else {
					errorMsg += ": " + string(body)
				}
			}
			return "", fmt.Errorf(errorMsg)
		}

		var statusResp TranscriptStatusResponse
		if err := json.Unmarshal(body, &statusResp); err != nil {
			return "", fmt.Errorf("ошибка парсинга ответа: %w", err)
		}

		switch statusResp.Status {
		case "completed":
			return statusResp.Text, nil
		case "error":
			return "", fmt.Errorf("ошибка транскрипции: %s", statusResp.Error)
		}

		attempts++
	}

	return "", fmt.Errorf("транскрипция заняла слишком много времени")
}
