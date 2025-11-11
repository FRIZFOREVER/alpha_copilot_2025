package handlers

import (
	"database/sql"
	"encoding/json"
	"jabki/internal/client"
	"jabki/internal/database"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Stream struct {
	client *client.ModelClient
	db     *sql.DB
	logger *logrus.Logger
}

type streamIn struct{
	Question string `json:"question"`
	VoiceURL string `json:"voice_url"`
}

func (sh *Stream) Handler(c *fiber.Ctx) error {
	questionTime := time.Now().UTC()
	var messageIn messageIn
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

	if err = json.Unmarshal(c.Body(), &messageIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}

	messages, err := database.GetHistory(sh.db, chatID, sh.logger)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}
}