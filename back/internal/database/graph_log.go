package database

import (
	"database/sql"
	_ "embed"
	"time"

	"github.com/sirupsen/logrus"
)

//go:embed queries/update_graph_log.sql
var upgradeGraphLogQuery string

//go:embed queries/get_graph_log.sql
var getGraphLogQuery string

// GraphLog представляет структуру лога графа ответов.
type GraphLog struct {
	ID       int       `json:"id"`
	Tag      string    `json:"tag"`
	Message  string    `json:"message"`
	TimeUTC  time.Time `json:"log_time"`
	AnswerID int       `json:"answer_id"`
}

// GraphLogService - структура для работы с логами графов.
type GraphLogService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewGraphLogRepository - конструктор для GraphLogService.
func NewGraphLogRepository(db *sql.DB, logger *logrus.Logger) *GraphLogService {
	return &GraphLogService{
		db:     db,
		logger: logger,
	}
}

// UpdateGraphLog - метод для обновления лога графа.
func (s *GraphLogService) UpdateGraphLog(message string, tag string, answerID int) error {
	_, err := s.db.Exec(upgradeGraphLogQuery, message, tag, answerID)
	if err != nil {
		s.logger.WithError(err).Error("Failed to update graph log")
		return err
	}
	return nil
}

// GetGraphLog - метод для получения логов графа по answer_id.
func (s *GraphLogService) GetGraphLog(answerID int) ([]GraphLog, error) {
	rows, err := s.db.Query(getGraphLogQuery, answerID)
	if err != nil {
		s.logger.WithError(err).Error("Failed to query graph log")
		return nil, err
	}
	defer rows.Close()

	var logs []GraphLog
	for rows.Next() {
		var log GraphLog
		err := rows.Scan(&log.ID, &log.Tag, &log.Message, &log.TimeUTC)
		if err != nil {
			s.logger.WithError(err).Error("Failed to scan graph log")
			return nil, err
		}
		logs = append(logs, log)
	}

	if err = rows.Err(); err != nil {
		s.logger.WithError(err).Error("Error iterating graph log rows")
		return nil, err
	}

	return logs, nil
}

// GraphLogRepository - интерфейс для управления логами графов.
type GraphLogRepository interface {
	UpdateGraphLog(message string, tag string, answerID int) error
	GetGraphLog(answerID int) ([]GraphLog, error)
}
