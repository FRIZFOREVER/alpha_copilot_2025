package handlers

import (
	"encoding/json"
	"errors"
	"jabki/internal/database"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Chat struct {
	repo   database.ChatManager
	logger *logrus.Logger
}

func NewChat(repo database.ChatManager, logger *logrus.Logger) *Chat {
	return &Chat{
		repo:   repo,
		logger: logger,
	}
}

type createChatIn struct {
	Name string `json:"name"`
}

type createChatOut struct {
	ChatID int `json:"chat_id"`
}

func (ch *Chat) CreateHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)
	var chatIn createChatIn
	var err error

	if err = json.Unmarshal(c.Body(), &chatIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}

	chatID, err := ch.repo.CreateChat(chatIn.Name, userUUID.String())
	if err != nil {
		if errors.Is(err, database.ErrUserNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error":   "User not found",
				"details": err.Error(),
			})
		}
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error creating chat",
			"details": err.Error(),
		})
	}

	return c.Status(fiber.StatusCreated).JSON(createChatOut{
		ChatID: chatID,
	})
}

func (ch *Chat) GetHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	chats, err := ch.repo.GetChats(userUUID.String())
	if err != nil {
		ch.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("failed to get chats from database")

		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to retrieve chats",
			"details": err.Error(),
		})
	}

	// Если чатов нет, возвращаем пустой массив вместо null
	if chats == nil {
		chats = []database.Chat{}
	}

	ch.logger.WithFields(logrus.Fields{
		"user_uuid":  userUUID,
		"chat_count": len(chats),
	}).Debug("chats retrieved successfully")

	return c.JSON(chats)
}

func (ch *Chat) RenameHandler(c *fiber.Ctx) error {
	chatIDStr := c.Params("chat_id")
	var chatIn createChatIn
	var err error

	chatID, err := strconv.Atoi(chatIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid chat ID format",
		})
	}

	if err = json.Unmarshal(c.Body(), &chatIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}

	if err = ch.repo.RenameChat(chatID, chatIn.Name); err != nil {
		if errors.Is(err, database.ErrUserNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error":   "User not found",
				"details": err.Error(),
			})
		}
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error creating chat",
			"details": err.Error(),
		})
	}

	return c.Status(fiber.StatusCreated).JSON(createChatOut{
		ChatID: chatID,
	})
}
