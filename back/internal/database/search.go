package database

import (
	"database/sql"
	_ "embed"
	"time"

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

type Search struct {
	QuestionID      int       `json:"question_id"`
	AnswerID        int       `json:"answer_id"`
	Question        string    `json:"question"`
	QuestionTag     *string   `json:"tag"`
	Answer          string    `json:"answer"`
	QuestionTime    time.Time `json:"question_time"`
	AnswerTime      time.Time `json:"answer_time"`
	VoiceURL        string    `json:"voice_url"`
	QuestionFileURL string    `json:"question_file_url"`
	Rating          *int      `json:"rating"`
	AnswerFileURL   string    `json:"answer_file_url"`
	ChatID          int       `json:"chat_id"`
}

// GetSearchedMessages - метод для поиска сообщений.
func (s *SearchService) GetSearchedMessages(uuid string, searchQuery string) ([]Search, error) {
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

	var search []Search
	for rows.Next() {
		var srch Search
		err := rows.Scan(
			&srch.QuestionID,
			&srch.AnswerID,
			&srch.Question,
			&srch.Answer,
			&srch.QuestionTime,
			&srch.AnswerTime,
			&srch.VoiceURL,
			&srch.QuestionFileURL,
			&srch.Rating,
			&srch.AnswerFileURL,
			&srch.ChatID,
		)
		if err != nil {
			s.logger.WithError(err).Error("Failed to scan row")
			continue
		}
		search = append(search, srch)
	}

	if err = rows.Err(); err != nil {
		s.logger.WithError(err).Error("Error during rows iteration")
		return nil, err
	}

	return search, nil
}

// SearchManager - интерфейс для поиска сообщений.
type SearchManager interface {
	GetSearchedMessages(uuid string, searchQuery string) ([]Search, error)
}
