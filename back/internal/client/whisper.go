package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/sirupsen/logrus"
)

type WhisperClient struct {
	method string
	host   string
	path   string
	client *http.Client
	logger *logrus.Logger
}

// NewWhisperClient создает новый клиент.
func NewWhisperClient(method, host, path string, logger *logrus.Logger) *WhisperClient {
	return &WhisperClient{
		method: method,
		host:   host,
		path:   path,
		client: &http.Client{
			Timeout: 0, // Без таймаута для long-polling соединений
		},
		logger: logger,
	}
}

type WhisperIn struct {
	VoiceURL string `json:"voice_url"`
}

type WhisperOut struct {
	Message  string `json:"message"`
	VoiceURL string `json:"voice_url"`
}

func (wc *WhisperClient) SendVoice(voiceURL []byte) (*WhisperOut, error) {
	fullURL := wc.host + wc.path
	wc.logger.Infof("Sending whisper request to %s", fullURL)

	req, err := http.NewRequest(wc.method, fullURL, bytes.NewReader(voiceURL))
	if err != nil {
		return nil, fmt.Errorf("create request error: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := wc.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("whisper request error: %w", err)
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			println("Ошибка при закрытии тела запроса: ", err.Error())
		}
	}()

	respBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read whisper response: %w", err)
	}

	// Логи
	wc.logger.Debugf("Whisper raw response: %s", string(respBytes))

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("whisper server returned status %d: %s",
			resp.StatusCode, string(respBytes))
	}

	var wr WhisperOut
	if err := json.Unmarshal(respBytes, &wr); err != nil {
		return nil, fmt.Errorf("unmarshal whisper response: %w", err)
	}

	return &wr, nil
}

func (wc *WhisperClient) Ping() (out bool) {
	resp, err := http.Get(wc.host + "/ping")
	if err != nil {
		// fmt.Println("Ошибка запроса:", err)
		out = false
	} else {
		if resp.StatusCode == http.StatusOK {
			wc.logger.Debug("OK:", resp.StatusCode)
			out = true
		} else {
			wc.logger.Debug("Не OK:", resp.StatusCode)
			out = false
		}
		if err := resp.Body.Close(); err != nil {
			wc.logger.Error("Ошибка при закрытии тела запроса: ", err)
		}
	}
	return out
}

type Whisperer interface {
	SendVoice(voiceURL []byte) (*WhisperOut, error)
}
