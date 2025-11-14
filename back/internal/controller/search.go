package controller

import (
	database "jabki/internal/repository"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Search struct {
	service *service.Search
	logger  *logrus.Logger
}

func NewSearch(service *service.Search, logger *logrus.Logger) *Search {
	return &Search{
		service: service,
		logger:  logger,
	}
}

func (sh *Search) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)
	pattern := c.Query("pattern")

	messages, err := database.GetSerchedMessages(sh.db, uuid.String(), pattern, sh.logger)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error in database",
			"details": err.Error(),
		})
	}

	return c.JSON(messages)
}
