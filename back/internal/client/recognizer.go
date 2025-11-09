package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
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
	fullURL := c.baseURL + c.path + "/upload"
	
	req, err := http.NewRequest("POST", fullURL, bytes.NewBuffer(audioData))
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", c.apiKey)
	req.Header.Set("Content-Type", "application/octet-stream")

	resp, err := c.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("ошибка загрузки: статус %d", resp.StatusCode)
	}

	var uploadResp UploadResponse
	if err := json.NewDecoder(resp.Body).Decode(&uploadResp); err != nil {
		return "", err
	}

	return uploadResp.UploadURL, nil
}

func (c *RecognizerClient) requestTranscript(uploadURL string) (string, error) {
	fullURL := c.baseURL + c.path + "/transcript"
	
	transcriptReq := TranscriptRequest{
		AudioURL:     uploadURL,
		LanguageCode: "ru",
	}

	jsonData, err := json.Marshal(transcriptReq)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", fullURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", c.apiKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("ошибка запроса транскрипции: статус %d", resp.StatusCode)
	}

	var transcriptResp TranscriptResponse
	if err := json.NewDecoder(resp.Body).Decode(&transcriptResp); err != nil {
		return "", err
	}

	return transcriptResp.ID, nil
}

func (c *RecognizerClient) waitForTranscript(transcriptID string) (string, error) {
	fullURL := c.baseURL + c.path + "/transcript/" + transcriptID
	
	maxAttempts := 30
	attempts := 0

	for attempts < maxAttempts {
		time.Sleep(1 * time.Second)

		req, err := http.NewRequest("GET", fullURL, nil)
		if err != nil {
			return "", err
		}

		req.Header.Set("Authorization", c.apiKey)

		resp, err := c.client.Do(req)
		if err != nil {
			return "", err
		}

		var statusResp TranscriptStatusResponse
		if err := json.NewDecoder(resp.Body).Decode(&statusResp); err != nil {
			resp.Body.Close()
			return "", err
		}
		resp.Body.Close()

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
