package handlers

import (
	"database/sql"
	"errors"
	"jabki/internal/database"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Profile struct {
	db     *sql.DB
	logger *logrus.Logger
}

func NewProfile(db *sql.DB, logger *logrus.Logger) *Profile {
	return &Profile{
		db:     db,
		logger: logger,
	}
}

func (ph *Profile) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)

	profile, err := database.GetProfile(ph.db, uuid.String(), ph.logger)
	if err != nil {
		if errors.Is(err, database.ErrUserNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error":   "User not found",
				"details": err.Error(),
			})
		}
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error get user profile",
			"details": err.Error(),
		})
	}

	return c.Status(fiber.StatusCreated).JSON(profile)
}