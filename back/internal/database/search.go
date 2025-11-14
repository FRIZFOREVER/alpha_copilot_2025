package database

import (
	"database/sql"
	_ "embed"

	"github.com/sirupsen/logrus"
)

//go:embed queries/search_message.sql
var searchMessageQuery string

// SearchService - структура для поиска сообщений.
type SearchService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewSearchRepository - конструктор для SearchService.
func NewSearchRepository(db *sql.DB, logger *logrus.Logger) *SearchService {
	return &SearchService{
		db:     db,
		logger: logger,
	}
}

// GetSearchedMessages - метод для поиска сообщений.
func (s *SearchService) GetSearchedMessages(uuid string, searchQuery string) ([]Message, error) {
	rows, err := s.db.Query(searchMessageQuery, uuid, searchQuery)
	if err != nil {
		s.logger.WithError(err).Error("Failed to query search")
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			s.logger.Error("Ошибка закрытия строк: ", err)
		}
	}()

	var messages []Message
	for rows.Next() {
		var msg Message
		err := rows.Scan(
			&msg.QuestionID,
			&msg.AnswerID,
			&msg.Question,
			&msg.Answer,
			&msg.QuestionTime,
			&msg.AnswerTime,
			&msg.VoiceURL,
			&msg.FileURL,
			&msg.Rating,
		)
		if err != nil {
			s.logger.WithError(err).Error("Failed to scan row")
			continue
		}
		messages = append(messages, msg)
	}

	if err = rows.Err(); err != nil {
		s.logger.WithError(err).Error("Error during rows iteration")
		return nil, err
	}

	return messages, nil
}

// SearchManager - интерфейс для поиска сообщений.
type SearchManager interface {
	GetSearchedMessages(uuid string, searchQuery string) ([]Message, error)
}
