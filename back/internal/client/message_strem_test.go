package client

import (
	"fmt"
	"log"
	"testing"
)

func TestMessageStream(t *testing.T) {
	client := NewStreamMessageClient("POST", "http://localhost:8000", "/message_stream")

	// Создаем payload с правильной структурой
	payload := PayloadStream{
		Messages: []struct {
			Role    string `json:"role"`
			Content string `json:"content"`
		}{
			{Role: "user", Content: "Hello! How are you?"},
		},
	}

	// Получаем канал для чтения StreamMessage
	messageChan, err := client.StreamRequestToModel(payload)
	if err != nil {
		log.Fatal("Failed to start stream:", err)
	}

	// Читаем сообщения из канала
	for message := range messageChan {
		if message != nil {
			fmt.Printf("Model: %s\n", message.Model)
			fmt.Printf("Done: %t\n", message.Done)
			fmt.Printf("Thinking: %s\n", message.Message.Thinking)
			fmt.Printf("Content: %s\n", message.Message.Content)
			fmt.Printf("Created At: %s\n", message.CreatedAt)
			fmt.Println("---")

			// Проверяем завершение стрима
			if message.Done {
				fmt.Println("Stream completed")
				break
			}
		}
	}
}
