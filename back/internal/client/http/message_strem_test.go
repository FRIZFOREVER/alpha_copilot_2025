package client

import (
	"fmt"
	"jabki/internal/domain/model"
	"log"
	"testing"

	"github.com/sirupsen/logrus"
)

func TestMessageStream(t *testing.T) {
	client := NewStreamClient("POST", "http://localhost:8000", "/message_stream", 5, logrus.New())

	// Создаем payload с правильной структурой
	payload := model.PayloadStream{
		Messages: []model.MessageHistory{
			{Role: "user", Content: "напиши hello world на java"},
		},
		Tag:    "",
		Mode:   "",
		System: "",
	}

	// Получаем канал для чтения StreamMessage
	messageChan, _, err := client.StreamRequestToModel(payload)
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
