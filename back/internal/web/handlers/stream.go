package handlers

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"jabki/internal/client"
	"jabki/internal/database"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Stream struct {
	client     *client.StreamMessageClient
	db         *sql.DB
	historyLen int
	logger     *logrus.Logger
}

func NewStream(client *client.StreamMessageClient, db *sql.DB, historyLen int, logger *logrus.Logger) *Stream {
	return &Stream{
		client:     client,
		db:         db,
		historyLen: historyLen,
		logger:     logger,
	}
}

type streamIn struct {
	Question string `json:"question"`
	VoiceURL string `json:"voice_url"`
	Tag      string `json:"tag"`
}

func (sh *Stream) Handler(c *fiber.Ctx) error {

	c.Set("Content-Type", "text/event-stream")
	c.Set("Cache-Control", "no-cache")
	c.Set("Connection", "keep-alive")

	// Получаем ResponseWriter для Flush
	w, ok := c.Context().Response.BodyWriter().(http.Flusher)
	if !ok {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Streaming not supported",
		})
	}

	questionTime := time.Now().UTC()
	var streamIn streamIn
	var err error

	uuid := c.Locals("uuid").(uuid.UUID)
	chatIDStr := c.Params("chat_id")

	chatID, err := strconv.Atoi(chatIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid chat ID format",
		})
	}

	isCorresponds, err := database.CheckChat(sh.db, uuid.String(), chatID, sh.logger)
	if err != nil || !isCorresponds {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Chat ID is not corresponds to user uuid",
		})
	}

	if err = json.Unmarshal(c.Body(), &streamIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}

	messages, err := database.GetHistory(sh.db, chatID, uuid.String(), sh.logger, sh.historyLen)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}

	var messageToModel client.PayloadStream
	for _, message := range messages {
		messageToModel.Messages = append(messageToModel.Messages,
			client.Message{
				Role:    "user",
				Content: message.Question,
			},
			client.Message{
				Role:    "assistant",
				Content: message.Answer,
			},
		)
	}

	messageToModel.Messages = append(messageToModel.Messages, client.Message{
		Role:    "user",
		Content: streamIn.Question,
	})

	questionID, answerID, err := database.WriteMessage(
		sh.db,
		chatID,
		streamIn.Question,
		"", //
		questionTime,
		questionTime, //
		streamIn.VoiceURL,
		sh.logger,
	)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error write message to DB",
			"details": err.Error(),
		})
	}

	messageToModel.Tag = streamIn.Tag

	messageChan, err := sh.client.StreamRequestToModel(messageToModel)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error start stream",
			"details": err.Error(),
		})
	}

	// отправляй тут метадату
	metaOut := streamMetaOut{
		QuestionID:   questionID,
		AnswerID:     answerID,
		QuestionTime: questionTime,
		Tag:          streamIn.Tag,
	}

	metaJSON, err := json.Marshal(metaOut)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Error encoding metadata",
			"details": err.Error(),
		})
	}

	// Отправка метаданных
	if _, err := c.Write(metaJSON); err != nil {
		return err
	}
	w.Flush()

	var builder strings.Builder
	builder.Grow(1024)
	for message := range messageChan {
		if message != nil {
			builder.WriteString(message.Message.Content)

			// отправляй чанк
			chunkOut := streamChunckOut{
				Content:  message.Message.Content,
				Thinking: message.Message.Thinking, // предполагая, что есть такое поле
				Time:     time.Now().UTC(),
				Done:     false,
			}
			
			chunkJSON, err := json.Marshal(chunkOut)
			if err != nil {
				sh.logger.Errorf("Error encoding chunk: %v", err)
				continue
			}
			
			if _, err := c.Write([]byte(fmt.Sprintf("data: %s\n\n", chunkJSON))); err != nil {
				sh.logger.Errorf("Error writing chunk: %v", err)
				break
			}
			w.Flush()

			if message.Done {
				// Отправляем финальный чанк с флагом Done
				finalChunk := streamChunckOut{
					Content:  "", // или итоговый контент если нужен
					Thinking: "",
					Time:     time.Now().UTC(),
					Done:     true,
				}
				
				finalJSON, err := json.Marshal(finalChunk)
				if err != nil {
					sh.logger.Errorf("Error encoding final chunk: %v", err)
				} else {
					c.Write([]byte(fmt.Sprintf("data: %s\n\n", finalJSON)))
					w.Flush()
				}
				break
			}
		}
	}

	// Сохраняем полный ответ в базу данных
	fullAnswer := builder.String()
	_, err = database.UpdateAnswer(sh.db, answerID, fullAnswer, sh.logger)
	if err != nil {
		sh.logger.Errorf("Error updating answer in database: %v", err)
	}

	return nil

}

type streamMetaOut struct {
	QuestionID   int       `json:"question_id"`
	AnswerID     int       `json:"answer_id"`
	QuestionTime time.Time `json:"question_time"`
	Tag          string    `json:"tag"`
}

type streamChunckOut struct {
	Content  string    `json:"content"`
	Thinking string    `json:"thinking"`
	Time     time.Time `json:"time"`
	Done     bool      `json:"Done"`
}
