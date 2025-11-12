package handlers

import (
	"database/sql"
	"encoding/json"
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

func (ph *Profile) GetHandler(c *fiber.Ctx) error {
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

type OtherInfo struct {
	UserInfo               string `json:"user_info"`
	BusinessInfo           string `json:"business_info"`
	AdditionalInstructions string `json:"additional_instructions"`
}

func (ph *Profile) PutOtherInfoHandler(c *fiber.Ctx) error {
	var info OtherInfo
	uuid := c.Locals("uuid").(uuid.UUID)

	if err := json.Unmarshal(c.Body(), &info); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}

	if err := database.UpdateOtherProfileInfo(
		ph.db,
		uuid.String(),
		info.UserInfo,
		info.BusinessInfo,
		info.AdditionalInstructions,
		ph.logger,
	); err != nil {
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

	return c.Status(fiber.StatusOK).Send([]byte(""))
}
