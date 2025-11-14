package controller

import (
	"encoding/json"
	"jabki/internal/domain/dto"
	"jabki/internal/service"
	"jabki/pkg"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
)

type Auth struct {
	service *service.Auth
	secret  string
	logger  *logrus.Logger
}

func NewAuth(service *service.Auth, secret string, logger *logrus.Logger) *Auth {
	return &Auth{
		service: service,
		secret:  secret,
		logger:  logger,
	}
}

func (ah *Auth) Handler(c *fiber.Ctx) (err error) {
	var authIn dto.AuthIn
	if err = json.Unmarshal(c.Body(), &authIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}
	var authOut dto.AuthOut

	userUUID, err := database.AuthenticatUser(ah.db, authIn.Login, authIn.Password, ah.logger)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "fail authentication",
			"details": err.Error(),
		})
	}

	authOut.Jwt = pkg.GetJWT(userUUID.String(), ah.secret)

	return c.JSON(authOut)
}
