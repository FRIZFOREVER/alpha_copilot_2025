package handlers

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"fmt"
	"jabki/internal/client"
	"jabki/internal/database"
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
	FileURL  string `json:"file_url"`
	Tag      string `json:"tag"`
	Mode     string `json:"mode"`
}

func (sh *Stream) Handler(c *fiber.Ctx) error {
	c.Set("Content-Type", "text/event-stream")
	c.Set("Cache-Control", "no-cache")
	c.Set("Connection", "keep-alive")
	c.Set("Transfer-Encoding", "chunked")

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

	messages, err := database.GetHistory(sh.db, chatID, uuid.String(), sh.logger, sh.historyLen, streamIn.Tag)
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
				ID:      message.QuestionID,
				Role:    "user",
				Content: message.Question,
			},
			client.Message{
				ID:      message.AnswerID,
				Role:    "assistant",
				Content: message.Answer,
			},
		)
	}

	questionID, answerID, err := database.WriteMessage(
		sh.db,
		chatID,
		streamIn.Question,
		"", //
		questionTime,
		questionTime, //
		streamIn.Tag,
		streamIn.VoiceURL,
		streamIn.FileURL,
		sh.logger,
	)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error write message to DB",
			"details": err.Error(),
		})
	}

	messageToModel.Messages = append(messageToModel.Messages, client.Message{
		ID:      questionID,
		Role:    "user",
		Content: streamIn.Question,
	})

	messageToModel.Tag = streamIn.Tag

	messageToModel.IsVoice = len(streamIn.VoiceURL) > 0

	messageToModel.FileURL = streamIn.FileURL

	messageToModel.ChatID = chatIDStr

	messageToModel.Mode = streamIn.Mode

	messageChan, tag, err := sh.client.StreamRequestToModel(messageToModel)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error start stream",
			"details": err.Error(),
		})
	}

	// Используем SetBodyStreamWriter для потоковой отправки
	c.Context().SetBodyStreamWriter(func(w *bufio.Writer) {
		// Отправка метаданных
		metaOut := streamMetaOut{
			QuestionID:   questionID,
			AnswerID:     answerID,
			QuestionTime: questionTime,
			Tag:          streamIn.Tag,
		}

		metaJSON, err := json.Marshal(metaOut)
		if err != nil {
			sh.logger.Errorf("Error encoding metadata: %v", err)
			return
		}

		// Отправляем метаданные как SSE событие
		if _, err := fmt.Fprintf(w, "data: %s\n\n", metaJSON); err != nil {
			sh.logger.Errorf("Error writing metadata: %v", err)
			return
		}
		w.Flush()

		var builder strings.Builder
		builder.Grow(1024)

		// Обрабатываем поток сообщений
		for message := range messageChan {
			if message != nil {
				builder.WriteString(message.Message.Content)

				// Отправляем чанк
				chunkOut := streamChunckOut{
					Content: message.Message.Content,
					Time:    time.Now().UTC(),
					Done:    false,
				}

				chunkJSON, err := json.Marshal(chunkOut)
				if err != nil {
					sh.logger.Errorf("Error encoding chunk: %v", err)
					continue
				}

				if _, err := fmt.Fprintf(w, "data: %s\n\n", chunkJSON); err != nil {
					sh.logger.Errorf("Error writing chunk: %v", err)
					break
				}
				w.Flush()

				if message.Done {
					// Отправляем финальный чанк с флагом Done
					finalChunk := streamChunckOut{
						Content: "",
						Time:    time.Now().UTC(),
						Done:    true,
					}

					finalJSON, err := json.Marshal(finalChunk)
					if err != nil {
						sh.logger.Errorf("Error encoding final chunk: %v", err)
					} else {
						fmt.Fprintf(w, "data: %s\n\n", finalJSON)
						w.Flush()
					}
					break
				}
			}
		}

		if tag == streamIn.Tag {
			// Сохраняем полный ответ в базу данных
			fullAnswer := builder.String()
			_, err = database.UpdateAnswer(sh.db, answerID, fullAnswer, sh.logger)
			if err != nil {
				sh.logger.Errorf("Error updating answer in database: %v", err)
			}
		} else {
			if tag == "" {
				tag = streamIn.Tag
			}
			// Сохраняем полный ответ в базу данных
			fullAnswer := builder.String()
			_, err = database.UpdateAnswerAndQuestionTag(sh.db, answerID, questionID, fullAnswer, tag, sh.logger)
			if err != nil {
				sh.logger.Errorf("Error updating answer and question tag in database: %v", err)
			}
		}
	})

	return nil
}

type streamMetaOut struct {
	QuestionID   int       `json:"question_id"`
	AnswerID     int       `json:"answer_id"`
	QuestionTime time.Time `json:"question_time"`
	Tag          string    `json:"tag"`
}

type streamChunckOut struct {
	Content string    `json:"content"`
	Time    time.Time `json:"time"`
	Done    bool      `json:"done"`
}
