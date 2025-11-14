package controller

import (
	"encoding/json"
	"jabki/internal/domain/dto"
	database "jabki/internal/repository"
	"jabki/pkg"

	"github.com/go-delve/delve/service"
	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
)

type Reg struct {
	service *service.Server
	secret  string
	logger  *logrus.Logger
}

func NewReg(service *service.Server, secret string, logger *logrus.Logger) *Reg {
	return &Reg{
		service: service,
		secret:  secret,
		logger:  logger,
	}
}

func (rh *Reg) Handler(c *fiber.Ctx) error {
	var regIn dto.RegIn
	var err error
	if err = json.Unmarshal(c.Body(), &regIn); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Invalid JSON format",
			"details": err.Error(),
		})
	}
	var regOut dto.RegOut

	userUUID, err := database.RegistrateUser(rh.db, regIn.Login, regIn.Password, regIn.FIO, rh.logger)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "fail registration",
			"details": err.Error(),
		})
	}

	regOut.Jwt = pkg.GetJWT(userUUID.String(), rh.secret)

	return c.JSON(regOut)
}
