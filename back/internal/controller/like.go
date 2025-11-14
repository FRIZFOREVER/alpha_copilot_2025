package controller

import (
	"encoding/json"
	"jabki/internal/domain/dto"
	database "jabki/internal/repository"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Like struct {
	service *service.Like
	logger  *logrus.Logger
}

func NewLike(service *service.Like, logger *logrus.Logger) *Like {
	return &Like{
		servcie: service,
		logger:  logger,
	}
}

func (lh *Like) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)
	chatIDStr := c.Params("chat_id")
	var likeIn dto.LikeIn
	var err error

	chatID, err := strconv.Atoi(chatIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid chat ID format",
		})
	}

	isCorresponds, err := database.CheckChat(lh.db, uuid.String(), chatID, lh.logger)
	if err != nil || !isCorresponds {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Chat ID is not corresponds to user uuid",
		})
	}

	if err = json.Unmarshal(c.Body(), &likeIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}

	if err = database.SetLike(lh.db, chatID, likeIn.AnswerID, likeIn.Rating, lh.logger); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}

	return c.SendString("")
}
