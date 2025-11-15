package database

import (
	"database/sql"
	_ "embed"
	"errors"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

//go:embed queries/authentication.sql
var authQuery string

var ErrUserNotFound = errors.New("user not found or invalid credentials")

// AuthService - структура для работы с аутентификацией.
type AuthService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewAuthService - конструктор для AuthService.
func NewAuthService(db *sql.DB, logger *logrus.Logger) *AuthService {
	return &AuthService{
		db:     db,
		logger: logger,
	}
}

// AuthenticateUser - метод для аутентификации пользователя.
func (s *AuthService) AuthenticateUser(login, password string) (*uuid.UUID, error) {
	var userUUID uuid.UUID

	err := s.db.QueryRow(authQuery, login, password).Scan(&userUUID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"login": login,
				"error": err,
			}).Warn("authentication failed: user not found or invalid password")
			return nil, ErrUserNotFound
		}

		s.logger.WithFields(logrus.Fields{
			"login": login,
			"error": err,
		}).Error("database error during authentication")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"login": login,
		"uuid":  userUUID.String(),
	}).Info("user authenticated successfully")

	return &userUUID, nil
}

// Authenticator - интерфейс для аутентификации пользователей.
type Authenticator interface {
	AuthenticateUser(login, password string) (*uuid.UUID, error)
}
