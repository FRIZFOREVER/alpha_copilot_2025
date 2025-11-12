package client

import (
	"fmt"
	"log"
	"testing"
)

func TestMessageStream(t *testing.T) {
	client := NewStreamMessageClient("POST", "http://localhost:8000", "/message_stream", 5)

	// Создаем payload с правильной структурой
	payload := PayloadStream{
		Messages: []Message{
			{Role: "user", Content: "напиши hello world на java"},
		},
		Tag:        "",
		Mode:       "",
		System:     "",
	}

	// Получаем канал для чтения StreamMessage
	messageChan, err := client.StreamRequestToModel(payload)
	if err != nil {
		log.Fatal("Failed to start stream:", err)
	}

	// Читаем сообщения из канала
	for message := range messageChan {
		if message != nil {
			fmt.Print(message.Message.Content)
			// Проверяем завершение стрима
			if message.Done {
				break
			}
		}
	}
}
