package database

import (
	"database/sql"
	_ "embed"
	"errors"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

//go:embed queries/registration.sql
var regQuery string

var ErrUserAlreadyExists = errors.New("user with this login already exists")

// RegistrationService - структура для регистрации пользователей.
type RegistrationService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewRegistrationService - конструктор для RegistrationService.
func NewRegistrationService(db *sql.DB, logger *logrus.Logger) *RegistrationService {
	return &RegistrationService{
		db:     db,
		logger: logger,
	}
}

// RegistrateUser - метод для регистрации пользователя.
func (s *RegistrationService) RegistrateUser(login, password, fio string) (*uuid.UUID, error) {
	var userUUID uuid.UUID

	err := s.db.QueryRow(regQuery, login, password, fio).Scan(&userUUID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"login": login,
				"error": err,
			}).Warn("registration failed: user already exists")
			return nil, ErrUserAlreadyExists
		}

		s.logger.WithFields(logrus.Fields{
			"login": login,
			"error": err,
		}).Error("database error during registration")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"login": login,
		"uuid":  userUUID.String(),
	}).Info("user registered successfully")

	return &userUUID, nil
}

// RegistrationManager - интерфейс для регистрации пользователей.
type RegistrationManager interface {
	RegistrateUser(login, password, fio string) (*uuid.UUID, error)
}
