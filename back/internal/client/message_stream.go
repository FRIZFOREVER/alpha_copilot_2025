package client

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/sirupsen/logrus"
)

type Message struct {
	ID      int    `json:"id"`
	Role    string `json:"role"`
	Content string `json:"content"`
}

// Profile представляет структуру профиля пользователя.
type Profile struct {
	ID                     int     `json:"id"`
	Login                  string  `json:"login"`
	FIO                    string  `json:"username"`
	UserInfo               *string `json:"user_info"`
	BusinessInfo           *string `json:"business_info"`
	AdditionalInstructions *string `json:"additional_instructions"`
}

// PayloadStream структура для входных данных.
type PayloadStream struct {
	Messages  []Message `json:"messages"`
	ChatID    string    `json:"chat_id"`
	Tag       string    `json:"tag"`
	Mode      string    `json:"mode"`
	FileURL   string    `json:"file_url"`
	IsVoice   bool      `json:"is_voice"`
	Profile   Profile   `json:"profile"`
}

// StreamMessage представляет структуру сообщения из стрима.
type StreamMessage struct {
	Model              string         `json:"model"`
	CreatedAt          string         `json:"created_at"`
	Done               bool           `json:"done"`
	DoneReason         string         `json:"done_reason"`
	TotalDuration      *int64         `json:"total_duration"`
	LoadDuration       *int64         `json:"load_duration"`
	PromptEvalCount    *int           `json:"prompt_eval_count"`
	PromptEvalDuration *int64         `json:"prompt_eval_duration"`
	EvalCount          *int           `json:"eval_count"`
	EvalDuration       *int64         `json:"eval_duration"`
	Message            MessageContent `json:"message"`
}

// MessageContent представляет содержимое сообщения.
type MessageContent struct {
	Role      string      `json:"role"`
	Content   string      `json:"content"`
	Thinking  string      `json:"thinking"`
	Images    interface{} `json:"images"`
	ToolName  *string     `json:"tool_name"`
	ToolCalls interface{} `json:"tool_calls"`
}

// StreamMessageClient клиент для работы с потоковыми сообщениями.
type StreamMessageClient struct {
	method     string
	url        string
	path       string
	client     *http.Client
	HistoryLen int
	logger     *logrus.Logger
}

// NewStreamMessageClient создает новый клиент.
func NewStreamMessageClient(method, url, path string, historyLen int, logger *logrus.Logger) *StreamMessageClient {
	return &StreamMessageClient{
		method: method,
		url:    url,
		path:   path,
		client: &http.Client{
			Timeout: 0, // Без таймаута для long-polling соединений
		},
		HistoryLen: historyLen,
		logger:     logger,
	}
}

// StreamRequestToModel выполняет запрос и возвращает канал для чтения сообщений StreamMessage.
func (c *StreamMessageClient) StreamRequestToModel(payload PayloadStream) (<-chan *StreamMessage, string, error) {
	var tag string
	// Маршалим payload в JSON
	jsonData, err := json.Marshal(payload)
	if err != nil {
		return nil, tag, fmt.Errorf("failed to marshal payload: %w", err)
	}

	// Создаем HTTP запрос
	req, err := http.NewRequest(c.method, c.url+c.path, strings.NewReader(string(jsonData)))
	if err != nil {
		return nil, tag, fmt.Errorf("failed to create request: %w", err)
	}

	// Устанавливаем заголовки
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "text/event-stream")
	req.Header.Set("Cache-Control", "no-cache")
	req.Header.Set("Connection", "keep-alive")

	// Выполняем запрос
	resp, err := c.client.Do(req)
	if err != nil {
		return nil, tag, fmt.Errorf("failed to make request: %w", err)
	}
	tag = resp.Header.Get("Tag")
	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		if err := resp.Body.Close(); err != nil {
			c.logger.Error("Ошибка при закрытии тела запроса: ", err)
		}
		return nil, tag, fmt.Errorf("server returned status: %d", resp.StatusCode)
	}

	// Создаем канал для StreamMessage
	messageChan := make(chan *StreamMessage)

	// Запускаем горутину для обработки SSE потока
	go c.processSSEStream(resp, messageChan)

	return messageChan, tag, nil
}

// processSSEStream обрабатывает SSE поток и отправляет StreamMessage в канал.
func (c *StreamMessageClient) processSSEStream(resp *http.Response, messageChan chan<- *StreamMessage) {
	defer func() {
		if err := resp.Body.Close(); err != nil {
			c.logger.Error("Ошибка при закрытии тела запроса: ", err)
		}
	}()
	defer close(messageChan)

	reader := bufio.NewReader(resp.Body)

	for {
		// Читаем строку из потока
		line, err := reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				// Конец потока
				return
			}
			// В случае ошибки просто завершаем поток
			return
		}

		// Пропускаем пустые строки и строки с префиксом ":" (комментарии в SSE)
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, ":") {
			continue
		}

		// Обрабатываем только строки с данными (data:)
		if strings.HasPrefix(line, "data: ") {
			data := strings.TrimPrefix(line, "data: ")

			// Проверяем на [DONE] сообщение (обычно в конце стрима)
			if data == "[DONE]" {
				return
			}

			// Парсим JSON в StreamMessage
			var message StreamMessage
			if err := json.Unmarshal([]byte(data), &message); err != nil {
				// В случае ошибки парсинга пропускаем сообщение
				continue
			}

			// Отправляем сообщение в канал
			messageChan <- &message
		}
	}
}

// StreamRequestToModelWithTimeout версия с таймаутом.
func (c *StreamMessageClient) StreamRequestToModelWithTimeout(payload PayloadStream, timeout time.Duration) (<-chan *StreamMessage, string, error) {
	messageChan := make(chan *StreamMessage)

	streamChan, tag, err := c.StreamRequestToModel(payload)
	if err != nil {
		return nil, tag, err
	}

	go func() {
		defer close(messageChan)

		timer := time.NewTimer(timeout)
		defer timer.Stop()

		for {
			select {
			case message, ok := <-streamChan:
				if !ok {
					return
				}
				select {
				case messageChan <- message:
				case <-timer.C:
					return
				}
			case <-timer.C:
				return
			}
		}
	}()

	return messageChan, tag, nil
}
