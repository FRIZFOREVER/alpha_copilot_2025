package database

import (
	"database/sql"
	_ "embed"

	"github.com/sirupsen/logrus"
)

//go:embed queries/search_message.sql
var searchMessageQuery string

func GetSerchedMessages(
	db *sql.DB,
	uuid string,
	searchQuery string,
	logger *logrus.Logger,
) (
	messages []Message,
	err error,
) {
	rows, err := db.Query(searchMessageQuery, uuid, searchQuery)
	if err != nil {
		logger.WithError(err).Error("Failed to query search")
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			logger.Error("Ошибка закрытия строк: ", err)
		}
	}()

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
