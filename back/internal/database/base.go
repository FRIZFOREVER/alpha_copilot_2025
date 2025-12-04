package database

import (
	"database/sql"

	"github.com/sirupsen/logrus"
)

func checkChat(db *sql.DB, userUUID string, chatID int, logger *logrus.Logger) (bool, error) {
	var isCorresponds bool

	err := db.QueryRow(checkChatQuery, userUUID, chatID).Scan(&isCorresponds)
	if err != nil {
		if err == sql.ErrNoRows {
			// Если запрос не вернул строк, считаем что чат не соответствует пользователю
			return false, nil
		}
		logger.WithError(err).Error("failed to check chat ownership")
		return false, err
	}

	return isCorresponds, nil
}

// GetHistory - метод для получения истории сообщений.
func getHistory(
	db *sql.DB,
	chatID int,
	uuid string,
	historyLen int,
	tag string,
	logger *logrus.Logger,
) ([]Message, error) {
	var rows *sql.Rows
	var err error

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
			&msg.QuestionTag,
			&msg.FileURL,
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
