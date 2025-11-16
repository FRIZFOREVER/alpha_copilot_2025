package handlers

import (
	"encoding/json"
	"jabki/internal/database"
	"jabki/pkg"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
)

type Auth struct {
	repo   database.Authenticator
	secret string
	logger *logrus.Logger
}

func NewAuth(repo database.Authenticator, secret string, logger *logrus.Logger) *Auth {
	return &Auth{
		repo:   repo,
		secret: secret,
		logger: logger,
	}
}

type authIn struct {
	Login    string `json:"login"`
	Password string `json:"password"`
}

func (ah *Auth) Handler(c *fiber.Ctx) (err error) {
	var authIn authIn
	if err = json.Unmarshal(c.Body(), &authIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}
	var authOut authOut

	userUUID, err := ah.repo.AuthenticateUser(authIn.Login, authIn.Password)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "fail authentication",
			"details": err.Error(),
		})
	}

	authOut.Jwt = pkg.GetJWT(userUUID.String(), ah.secret)

	return c.JSON(authOut)
}

type authOut struct {
	Jwt string `json:"jwt"`
}
