package client

import (
	"time"
)

type Recognizer interface {
	// MessageToRecognizer отправляет аудиоданные на распознавание и возвращает текст
	// Возвращает распознанный текст или ошибку в случае неудачи
	MessageToRecognizer(audioData []byte) (string, error)
}

// StreamMessageProcessor интерфейс для работы с потоковыми сообщениями.
type StreamMessageProcessor interface {
	// StreamRequestToModel выполняет запрос и возвращает канал для чтения сообщений StreamMessage
	// Возвращает канал сообщений, тег из заголовков ответа и ошибку
	StreamRequestToModel(payload PayloadStream) (<-chan *StreamMessage, string, error)

	// StreamRequestToModelWithTimeout выполняет запрос с таймаутом
	// Возвращает канал сообщений, тег из заголовков ответа и ошибку
	StreamRequestToModelWithTimeout(payload PayloadStream, timeout time.Duration) (<-chan *StreamMessage, string, error)
}
