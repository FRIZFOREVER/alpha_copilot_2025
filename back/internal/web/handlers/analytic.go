package handlers

import (
	"encoding/json"
	"errors"
	"jabki/internal/database"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Analytic struct {
	repo   database.Analytic
	logger *logrus.Logger
}

func NewAnalytic(repo database.Analytic, logger *logrus.Logger) *Analytic {
	return &Analytic{
		repo:   repo,
		logger: logger,
	}
}

// GetAverageLikesHandler - обработчик для получения средних оценок.
func (ah *Analytic) GetAverageLikesHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	averageLikes, err := ah.repo.GetAverageLikes(userUUID)
	if err != nil {
		if errors.Is(err, database.ErrAnalyticNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error": "Analytic data not found",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to get average likes",
			"details": err.Error(),
		})
	}

	return c.JSON(averageLikes)
}

// GetChatCountsHandler - обработчик для получения количества чатов.
func (ah *Analytic) GetChatCountsHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	chatCounts, err := ah.repo.GetChatCounts(userUUID)
	if err != nil {
		if errors.Is(err, database.ErrAnalyticNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error": "Analytic data not found",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to get chat counts",
			"details": err.Error(),
		})
	}

	return c.JSON(chatCounts)
}

// GetDayCountHandler - обработчик для получения количества дней активности.
func (ah *Analytic) GetDayCountHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	dayCount, err := ah.repo.GetDayCount(userUUID)
	if err != nil {
		if errors.Is(err, database.ErrAnalyticNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error": "Analytic data not found",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to get day count",
			"details": err.Error(),
		})
	}

	return c.JSON(dayCount)
}

// GetFileCountsHandler - обработчик для получения количества файлов.
func (ah *Analytic) GetFileCountsHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	fileCounts, err := ah.repo.GetFileCounts(userUUID)
	if err != nil {
		if errors.Is(err, database.ErrAnalyticNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error": "Analytic data not found",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to get file counts",
			"details": err.Error(),
		})
	}

	return c.JSON(fileCounts)
}

// GetMessageCountsHandler - обработчик для получения количества сообщений.
func (ah *Analytic) GetMessageCountsHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	messageCounts, err := ah.repo.GetMessageCounts(userUUID)
	if err != nil {
		if errors.Is(err, database.ErrAnalyticNotFound) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"error": "Analytic data not found",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to get message counts",
			"details": err.Error(),
		})
	}

	return c.JSON(messageCounts)
}

// GetTagCountsHandler - обработчик для получения статистики по тегам.
func (ah *Analytic) GetTagCountsHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	tagCounts, err := ah.repo.GetTagCounts(userUUID)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to get tag counts",
			"details": err.Error(),
		})
	}

	return c.JSON(tagCounts)
}

// GetTimeseriesMessagesHandler - обработчик для получения временных рядов сообщений.
func (ah *Analytic) GetTimeseriesMessagesHandler(c *fiber.Ctx) error {
	userUUID := c.Locals("uuid").(uuid.UUID)

	var request struct {
		StartDate string `json:"start_date"`
		EndDate   string `json:"end_date"`
	}

	if err := json.Unmarshal(c.Body(), &request); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}

	// Валидация дат
	if request.StartDate == "" || request.EndDate == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Start date and end date are required",
		})
	}

	// Проверка формата дат
	if _, err := time.Parse("2006-01-02", request.StartDate); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid start date format, expected YYYY-MM-DD",
			"details": err.Error(),
		})
	}

	if _, err := time.Parse("2006-01-02", request.EndDate); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid end date format, expected YYYY-MM-DD",
			"details": err.Error(),
		})
	}

	timeseries, err := ah.repo.GetTimeseriesMessages(userUUID, request.StartDate, request.EndDate)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to get timeseries messages",
			"details": err.Error(),
		})
	}

	return c.JSON(timeseries)
}
