package database

import (
	"database/sql"
	_ "embed"
	"time"

	"github.com/sirupsen/logrus"
)

//go:embed queries/like.sql
var likeyQuery string

// LikeService - структура для работы с лайками.
type LikeService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewLikeRepository - конструктор для LikeService.
func NewLikeRepository(db *sql.DB, logger *logrus.Logger) *LikeService {
	return &LikeService{
		db:     db,
		logger: logger,
	}
}

// SetLike - метод для установки лайка/рейтинга.
func (s *LikeService) SetLike(chatID int, answerID int, rating *int) error {
	startTime := time.Now()

	// Execute the SQL query
	result, err := s.db.Exec(likeyQuery, chatID, answerID, rating)
	if err != nil {
		s.logger.WithFields(logrus.Fields{
			"chatID":   chatID,
			"answerID": answerID,
			"error":    err,
			"duration": time.Since(startTime),
		}).Error("Failed to set like visibility")
		return err
	}

	// Check if any rows were affected
	rowsAffected, err := result.RowsAffected()
	if err != nil {
		s.logger.WithFields(logrus.Fields{
			"chatID":   chatID,
			"answerID": answerID,
			"error":    err,
			"duration": time.Since(startTime),
		}).Error("Failed to get rows affected after setting like")
		return err
	}

	s.logger.WithFields(logrus.Fields{
		"chatID":       chatID,
		"answerID":     answerID,
		"rowsAffected": rowsAffected,
		"duration":     time.Since(startTime),
	}).Info("Successfully set like visibility")

	return nil
}

// LikeRepository - интерфейс для управления лайками.
type LikeRepository interface {
	CheckChat(userUUID string, chatID int) (bool, error)
	SetLike(chatID int, answerID int, rating *int) error
}

func (s *LikeService) CheckChat(userUUID string, chatID int) (bool, error) {
	return checkChat(s.db, userUUID, chatID, s.logger)
}
