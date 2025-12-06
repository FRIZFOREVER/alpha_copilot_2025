package database

import (
	"database/sql"
	_ "embed"
	"time"

	"github.com/sirupsen/logrus"
)

//go:embed queries/history.sql
var historyQuery string

//go:embed queries/history_with_limit.sql
var historyWithLimitQuery string

//go:embed queries/hide_answers.sql
var hideAnswersQuery string

//go:embed queries/hide_questions.sql
var hideQuestionsQuery string

// Message представляет структуру сообщения.
type Message struct {
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
	AnswerFileURL   *string    `json:"answer_file_url"`
}

// HistoryService - структура для работы с историей сообщений.
type HistoryService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// CheckChat implements HistoryManager.
func (s *HistoryService) CheckChat(userUUID string, chatID int) (bool, error) {
	return checkChat(s.db, userUUID, chatID, s.logger)
}

// NewHistoryRepository - конструктор для HistoryService.
func NewHistoryRepository(db *sql.DB, logger *logrus.Logger) *HistoryService {
	return &HistoryService{
		db:     db,
		logger: logger,
	}
}

// GetHistory - метод для получения истории сообщений.
func (s *HistoryService) GetHistory(
	chatID int,
	uuid string,
	historyLen int,
	tag string,
) ([]Message, error) {
	return getHistory(s.db, chatID, uuid, historyLen, tag, s.logger)
}

// HideMessages - метод для скрытия сообщений чата.
func (s *HistoryService) HideMessages(chatID int) error {
	tx, err := s.db.Begin()
	if err != nil {
		s.logger.WithError(err).Error("Failed to begin transaction")
		return err
	}

	defer func() {
		if p := recover(); p != nil {
			if err := tx.Rollback(); err != nil {
				s.logger.Error("Ошибка отката транзакции: ", err)
			}
			panic(p)
		} else if err != nil {
			if err := tx.Rollback(); err != nil {
				s.logger.Error("Ошибка отката транзакции: ", err)
			}
		} else {
			err = tx.Commit()
			if err != nil {
				s.logger.WithError(err).Error("Failed to commit transaction")
			}
		}
	}()

	// Сначала скрываем ответы
	_, err = tx.Exec(hideAnswersQuery, chatID)
	if err != nil {
		s.logger.WithError(err).WithField("uuid", chatID).Error("Failed to hide answers")
		return err
	}

	// Затем скрываем вопросы
	_, err = tx.Exec(hideQuestionsQuery, chatID)
	if err != nil {
		s.logger.WithError(err).WithField("uuid", chatID).Error("Failed to hide questions")
		return err
	}

	s.logger.WithField("uuid", chatID).Info("User messages hidden successfully")
	return nil
}

// HistoryRepository - единый интерфейс для управления историей сообщений.
type HistoryRepository interface {
	GetHistory(chatID int, uuid string, historyLen int, tag string) ([]Message, error)
	HideMessages(chatID int) error
	CheckChat(userUUID string, chatID int) (bool, error)
}
