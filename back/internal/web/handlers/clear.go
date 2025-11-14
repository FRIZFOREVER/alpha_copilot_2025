package handlers

import (
	"jabki/internal/database"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Clear struct {
	repo   database.HistoryManager
	logger *logrus.Logger
}

func NewClear(repo database.HistoryManager, logger *logrus.Logger) *Clear {
	return &Clear{
		repo:   repo,
		logger: logger,
	}
}

func (ch *Clear) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)
	chatIDStr := c.Params("chat_id")

	chatID, err := strconv.Atoi(chatIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid chat ID format",
		})
	}

	isCorresponds, err := ch.repo.CheckChat(uuid.String(), chatID)
	if err != nil || !isCorresponds {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Chat ID is not corresponds to user uuid",
		})
	}

	if err := ch.repo.HideMessages(chatID); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}

	return c.SendString("")
}
