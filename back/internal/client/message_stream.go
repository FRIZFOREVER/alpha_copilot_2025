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
	ID                     int    `json:"id"`
	Login                  string `json:"login"`
	FIO                    string `json:"username"`
	UserInfo               string `json:"user_info"`
	BusinessInfo           string `json:"business_info"`
	AdditionalInstructions string `json:"additional_instructions"`
}

// PayloadStream структура для входных данных.
type PayloadStream struct {
	Messages []Message `json:"messages"`
	ChatID   int       `json:"chat_id"`
	Tag      string    `json:"tag"`
	Mode     string    `json:"mode"`
	FileURL  string    `json:"file_url"`
	IsVoice  bool      `json:"is_voice"`
	Profile  Profile   `json:"profile"`
}

// StreamMessage представляет структуру сообщения из стрима.
type StreamMessage struct {
	ID                string        `json:"id"`
	Choices           []ChoiceDelta `json:"choices"`
	Created           int64         `json:"created"`
	Model             string        `json:"model"`
	Object            string        `json:"object"`
	ServiceTier       *string       `json:"service_tier,omitempty"`
	SystemFingerprint *string       `json:"system_fingerprint,omitempty"`
	Usage             *UsageStats   `json:"usage,omitempty"`
	Provider          string        `json:"provider"`
	FileURL           *string       `json:"file_url,omitempty"`
}

// ChoiceDelta представляет выбор с дельтой изменений.
type ChoiceDelta struct {
	Delta              DeltaContent `json:"delta"`
	FinishReason       *string      `json:"finish_reason"`
	Index              int          `json:"index"`
	Logprobs           interface{}  `json:"logprobs"`
	NativeFinishReason *string      `json:"native_finish_reason,omitempty"`
}

// DeltaContent представляет инкрементальные изменения в сообщении.
type DeltaContent struct {
	Content          string            `json:"content"`
	FunctionCall     interface{}       `json:"function_call"`
	Refusal          interface{}       `json:"refusal"`
	Role             string            `json:"role"`
	ToolCalls        interface{}       `json:"tool_calls"`
	Reasoning        *string           `json:"reasoning"`
	ReasoningDetails []ReasoningDetail `json:"reasoning_details"`
}

// ReasoningDetail представляет детали reasoning.
type ReasoningDetail struct {
	Type   string `json:"type"`
	Text   string `json:"text"`
	Format string `json:"format"`
	Index  int    `json:"index"`
}

// UsageStats представляет статистику использования токенов.
type UsageStats struct {
	CompletionTokens        int                     `json:"completion_tokens"`
	PromptTokens            int                     `json:"prompt_tokens"`
	TotalTokens             int                     `json:"total_tokens"`
	CompletionTokensDetails CompletionTokensDetails `json:"completion_tokens_details"`
	PromptTokensDetails     PromptTokensDetails     `json:"prompt_tokens_details"`
	Cost                    float64                 `json:"cost"`
	IsByok                  bool                    `json:"is_byok"`
	CostDetails             CostDetails             `json:"cost_details"`
}

// CompletionTokensDetails представляет детали completion токенов.
type CompletionTokensDetails struct {
	AcceptedPredictionTokens *int `json:"accepted_prediction_tokens"`
	AudioTokens              *int `json:"audio_tokens"`
	ReasoningTokens          int  `json:"reasoning_tokens"`
	RejectedPredictionTokens *int `json:"rejected_prediction_tokens"`
	ImageTokens              int  `json:"image_tokens"`
}

// PromptTokensDetails представляет детали prompt токенов.
type PromptTokensDetails struct {
	AudioTokens  int `json:"audio_tokens"`
	CachedTokens int `json:"cached_tokens"`
	VideoTokens  int `json:"video_tokens"`
}

// CostDetails представляет детали стоимости.
type CostDetails struct {
	UpstreamInferenceCost            *float64 `json:"upstream_inference_cost"`
	UpstreamInferencePromptCost      float64  `json:"upstream_inference_prompt_cost"`
	UpstreamInferenceCompletionsCost float64  `json:"upstream_inference_completions_cost"`
}

// MessageContent представляет содержимое сообщения (для не-потоковых ответов).
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

		if resp.StatusCode == http.StatusUnprocessableEntity {
			b, _ := io.ReadAll(resp.Body)
			fmt.Println("---!!!АХТУНГ!!!--\n\n", string(b), "\n\n---!!!АХТУНГ!!!--")
		}

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

			if message.FileURL != nil {
				messageChan <- &message
				continue
			}

			if len(message.Choices) > 0 {
				if message.Choices[0].Delta.Content == "" {
					continue
				}
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
