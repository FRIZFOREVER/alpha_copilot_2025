package handlers

import (
	"jabki/internal/database"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Search struct {
	repo   database.SearchManager
	logger *logrus.Logger
}

func NewSearch(repo database.SearchManager, logger *logrus.Logger) *Search {
	return &Search{
		repo:   repo,
		logger: logger,
	}
}

func (sh *Search) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)
	pattern := c.Query("pattern")

	messages, err := sh.repo.GetSearchedMessages(uuid.String(), pattern)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}

	return c.JSON(messages)
}
