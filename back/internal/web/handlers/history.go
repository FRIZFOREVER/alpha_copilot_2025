package handlers

import (
	"jabki/internal/client"
	"jabki/internal/database"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type History struct {
	repo   database.HistoryRepository
	logger *logrus.Logger
}

func NewHistory(repo database.HistoryRepository, logger *logrus.Logger) *History {
	return &History{
		repo:   repo,
		logger: logger,
	}
}

func (hh *History) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)
	chatIDStr := c.Params("chat_id")

	chatID, err := strconv.Atoi(chatIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid chat ID format",
		})
	}

	isCorresponds, err := hh.repo.CheckChat(uuid.String(), chatID)
	if err != nil || !isCorresponds {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Chat ID is not corresponds to user uuid",
		})
	}

	messages, err := hh.repo.GetHistory(chatID, uuid.String(), -1, "")
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}

	authHeader := c.Get("Authorization")
	const prefix = "Token "
	if strings.HasPrefix(authHeader, prefix) {
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
		return c.JSON(messageToModel)
	}

	return c.JSON(messages)
}
