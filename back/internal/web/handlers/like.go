package handlers

import (
	"encoding/json"
	"jabki/internal/database"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Like struct {
	repo   database.LikeRepository
	logger *logrus.Logger
}

func NewLike(repo database.LikeRepository, logger *logrus.Logger) *Like {
	return &Like{
		repo:   repo,
		logger: logger,
	}
}

type likeIn struct {
	AnswerID int  `json:"answer_id"`
	Rating   *int `json:"rating"`
}

func (lh *Like) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)
	chatIDStr := c.Params("chat_id")
	var likeIn likeIn
	var err error

	chatID, err := strconv.Atoi(chatIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid chat ID format",
		})
	}

	isCorresponds, err := lh.repo.CheckChat(uuid.String(), chatID)
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

	if err = lh.repo.SetLike(chatID, likeIn.AnswerID, likeIn.Rating); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}

	return c.SendString("")
}
