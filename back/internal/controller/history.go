package controller

import (
	"jabki/internal/client"
	database "jabki/internal/repository"
	"jabki/internal/service"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type History struct {
	service *service.History
	logger  *logrus.Logger
}

func NewHistory(service *service.History, logger *logrus.Logger) *History {
	return &History{
		service: service,
		logger:  logger,
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

	isCorresponds, err := database.CheckChat(hh.db, uuid.String(), chatID, hh.logger)
	if err != nil || !isCorresponds {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Chat ID is not corresponds to user uuid",
		})
	}

	messages, err := database.GetHistory(hh.db, chatID, uuid.String(), hh.logger, -1, "")
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
