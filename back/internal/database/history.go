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

func GetHistory(
	db *sql.DB,
	chatID int,
	uuid string,
	logger *logrus.Logger,
	historyLen int,
	tag string,
) (
	messages []Message,
	err error,
) {
	var rows *sql.Rows

	if historyLen < 0 {
		rows, err = db.Query(historyQuery, chatID)
		if err != nil {
			logger.WithError(err).Error("Failed to query history")
			return nil, err
		}
		defer func() {
			if err := rows.Close(); err != nil {
				logger.Error("Ошибка закрытия строк: ", err)
			}
		}()
	} else {
		rows, err = db.Query(historyWithLimitQuery, uuid, historyLen, tag)
		if err != nil {
			logger.WithError(err).Error("Failed to query history")
			return nil, err
		}
		defer func() {
			if err := rows.Close(); err != nil {
				logger.Error("Ошибка закрытия строк: ", err)
			}
		}()
	}

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
			&msg.QuestionTag,
		)
		if err != nil {
			logger.WithError(err).Error("Failed to scan row")
			continue
		}
		messages = append(messages, msg)
	}

	if err = rows.Err(); err != nil {
		logger.WithError(err).Error("Error during rows iteration")
		return nil, err
	}

	return messages, nil
}

type Message struct {
	QuestionID   int       `json:"question_id"`
	AnswerID     int       `json:"answer_id"`
	Question     string    `json:"question"`
	QuestionTag  *string   `json:"tag"`
	Answer       string    `json:"answer"`
	QuestionTime time.Time `json:"question_time"`
	AnswerTime   time.Time `json:"answer_time"`
	VoiceURL     string    `json:"voice_url"`
	FileURL      string    `json:"file_url"`
	Rating       *int      `json:"rating"`
}
