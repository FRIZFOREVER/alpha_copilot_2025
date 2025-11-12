package database

import (
	"database/sql"
	_ "embed"
	"time"

	"github.com/sirupsen/logrus"
)

func WriteEmptyMessage(
	db *sql.DB,
	chatID int,
	questionTime, answerTime time.Time,
	voiceURL string,
	logger *logrus.Logger,
) (
	questionID int,
	answerID int,
	err error,
) {
	tx, err := db.Begin()
	if err != nil {
		logger.WithError(err).Error("Failed to begin transaction")
		return 0, 0, err
	}

	defer func() {
		if p := recover(); p != nil {
			tx.Rollback()
			panic(p)
		} else if err != nil {
			tx.Rollback()
		} else {
			err = tx.Commit()
			if err != nil {
				logger.WithError(err).Error("Failed to commit transaction")
			}
		}
	}()

	err = tx.QueryRow(answerQuery, answerTime, "", chatID).Scan(&answerID)
	if err != nil {
		logger.WithError(err).Error("Failed to insert answer")
		return 0, 0, err
	}
	logger.WithFields(logrus.Fields{
		"answer_id": answerID,
		"chat_id":   chatID,
	}).Info("Answer inserted successfully")

	err = tx.QueryRow(questionQuery, questionTime, "", chatID, answerID, voiceURL).Scan(&questionID)
	if err != nil {
		logger.WithError(err).Error("Failed to insert question")
		return 0, 0, err
	}

	logger.WithFields(logrus.Fields{
		"question_id": questionID,
		"chat_id":     chatID,
	}).Info("Question inserted successfully")

	return questionID, answerID, nil
}
