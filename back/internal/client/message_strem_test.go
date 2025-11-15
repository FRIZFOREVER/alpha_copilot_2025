package client

import (
	"fmt"
	"log"
	"testing"

	"github.com/sirupsen/logrus"
)

func TestMessageStream(t *testing.T) {
	client := NewStreamMessageClient("POST", "http://localhost:8000", "/message_stream", 5, logrus.New())

	// Создаем payload с правильной структурой
	payload := PayloadStream{
		Messages: []Message{
			{Role: "user", Content: "напиши hello world на javaf"},
		},
		Tag:    "",
		Mode:   "",
		System: "",
	}

	// Получаем канал для чтения StreamMessage
	messageChan, _, err := client.StreamRequestToModel(payload)
	if err != nil {
		if err.Error() == "failed to make request: Post \"http://localhost:8000/message_stream\": dial tcp [::1]:8000: connectex: No connection could be made because the target machine actively refused it." {
			return
		}
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
