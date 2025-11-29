package database

import (
	"database/sql"
	_ "embed"
	"errors"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

//go:embed queries/broad_analytic/average_likes.sql
var avgLikesQuery string

//go:embed queries/broad_analytic/count_chats.sql
var countChatsQuery string

//go:embed queries/broad_analytic/count_days.sql
var countDaysQuery string

//go:embed queries/broad_analytic/count_files.sql
var countFilesQuery string

//go:embed queries/broad_analytic/count_messages.sql
var countMessagesQuery string

//go:embed queries/broad_analytic/count_tags.sql
var countTagsQuery string

//go:embed queries/timeseries_analytic/timeseries_messages.sql
var timeseriesMessagesQuery string

var ErrAnalyticNotFound = errors.New("analytic data not found")

// AnalyticService - структура для работы с аналитикой.
type AnalyticService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewAnalyticRepository - конструктор для AnalyticService.
func NewAnalyticRepository(db *sql.DB, logger *logrus.Logger) *AnalyticService {
	return &AnalyticService{
		db:     db,
		logger: logger,
	}
}

// AverageLikes - структура для хранения средних оценок.
type AverageLikes struct {
	AvgRating          sql.NullFloat64 `json:"avg_rating"`
	AvgRatingYesterday sql.NullFloat64 `json:"avg_rating_yesterday"`
}

// GetAverageLikes - метод для получения средних оценок пользователя.
func (s *AnalyticService) GetAverageLikes(userUUID uuid.UUID) (*AverageLikes, error) {
	var result AverageLikes

	err := s.db.QueryRow(avgLikesQuery, userUUID).Scan(&result.AvgRating, &result.AvgRatingYesterday)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"user_uuid": userUUID,
				"error":     err,
			}).Warn("average likes not found")
			return nil, ErrAnalyticNotFound
		}

		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during getting average likes")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid": userUUID,
	}).Info("average likes retrieved successfully")

	return &result, nil
}

// ChatCounts - структура для хранения количества чатов.
type ChatCounts struct {
	CountChats          int `json:"count_chats"`
	CountChatsYesterday int `json:"count_chats_yesterday"`
}

// GetChatCounts - метод для получения количества чатов пользователя.
func (s *AnalyticService) GetChatCounts(userUUID uuid.UUID) (*ChatCounts, error) {
	var result ChatCounts

	err := s.db.QueryRow(countChatsQuery, userUUID).Scan(&result.CountChats, &result.CountChatsYesterday)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"user_uuid": userUUID,
				"error":     err,
			}).Warn("chat counts not found")
			return nil, ErrAnalyticNotFound
		}

		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during getting chat counts")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid": userUUID,
		"count":     result.CountChats,
	}).Info("chat counts retrieved successfully")

	return &result, nil
}

// DayCount - структура для хранения количества дней активности.
type DayCount struct {
	CountDays int `json:"count_days"`
}

// GetDayCount - метод для получения количества дней активности пользователя.
func (s *AnalyticService) GetDayCount(userUUID uuid.UUID) (*DayCount, error) {
	var result DayCount

	err := s.db.QueryRow(countDaysQuery, userUUID).Scan(&result.CountDays)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"user_uuid": userUUID,
				"error":     err,
			}).Warn("day count not found")
			return nil, ErrAnalyticNotFound
		}

		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during getting day count")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid": userUUID,
		"count":     result.CountDays,
	}).Info("day count retrieved successfully")

	return &result, nil
}

// FileCounts - структура для хранения количества файлов.
type FileCounts struct {
	CountFiles          int `json:"count_files"`
	CountFilesYesterday int `json:"count_files_yesterday"`
}

// GetFileCounts - метод для получения количества файлов пользователя.
func (s *AnalyticService) GetFileCounts(userUUID uuid.UUID) (*FileCounts, error) {
	var result FileCounts

	err := s.db.QueryRow(countFilesQuery, userUUID).Scan(&result.CountFiles, &result.CountFilesYesterday)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"user_uuid": userUUID,
				"error":     err,
			}).Warn("file counts not found")
			return nil, ErrAnalyticNotFound
		}

		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during getting file counts")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid": userUUID,
		"count":     result.CountFiles,
	}).Info("file counts retrieved successfully")

	return &result, nil
}

// MessageCounts - структура для хранения количества сообщений.
type MessageCounts struct {
	CountMessages          int `json:"count_messages"`
	CountMessagesYesterday int `json:"count_messages_yesterday"`
}

// GetMessageCounts - метод для получения количества сообщений пользователя.
func (s *AnalyticService) GetMessageCounts(userUUID uuid.UUID) (*MessageCounts, error) {
	var result MessageCounts

	err := s.db.QueryRow(countMessagesQuery, userUUID).Scan(&result.CountMessages, &result.CountMessagesYesterday)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"user_uuid": userUUID,
				"error":     err,
			}).Warn("message counts not found")
			return nil, ErrAnalyticNotFound
		}

		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during getting message counts")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid": userUUID,
		"count":     result.CountMessages,
	}).Info("message counts retrieved successfully")

	return &result, nil
}

// TagCount - структура для хранения тега и его количества.
type TagCount struct {
	Tag      string `json:"tag"`
	TagCount int    `json:"tag_count"`
}

// GetTagCounts - метод для получения статистики по тегам пользователя.
func (s *AnalyticService) GetTagCounts(userUUID uuid.UUID) ([]TagCount, error) {
	rows, err := s.db.Query(countTagsQuery, userUUID)
	if err != nil {
		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during getting tag counts")
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			s.logger.Error("Ошибка закрытия строк: ", err)
		}
	}()

	var tagCounts []TagCount
	for rows.Next() {
		var tagCount TagCount
		err := rows.Scan(&tagCount.Tag, &tagCount.TagCount)
		if err != nil {
			s.logger.WithFields(logrus.Fields{
				"user_uuid": userUUID,
				"error":     err,
			}).Error("error scanning tag count row")
			return nil, err
		}
		tagCounts = append(tagCounts, tagCount)
	}

	if err = rows.Err(); err != nil {
		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("error iterating tag count rows")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid": userUUID,
		"count":     len(tagCounts),
	}).Info("tag counts retrieved successfully")

	return tagCounts, nil
}

// TimeseriesMessage - структура для хранения данных временных рядов сообщений.
type TimeseriesMessage struct {
	Day           string `json:"day"`
	CountMessages int    `json:"count_messages"`
}

// GetTimeseriesMessages - метод для получения временных рядов сообщений пользователя.
func (s *AnalyticService) GetTimeseriesMessages(userUUID uuid.UUID, startDate, endDate string) ([]TimeseriesMessage, error) {
	rows, err := s.db.Query(timeseriesMessagesQuery, userUUID, startDate, endDate)
	if err != nil {
		s.logger.WithFields(logrus.Fields{
			"user_uuid":  userUUID,
			"start_date": startDate,
			"end_date":   endDate,
			"error":      err,
		}).Error("database error during getting timeseries messages")
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			s.logger.Error("Ошибка закрытия строк: ", err)
		}
	}()

	var timeseries []TimeseriesMessage
	for rows.Next() {
		var ts TimeseriesMessage
		err := rows.Scan(&ts.Day, &ts.CountMessages)
		if err != nil {
			s.logger.WithFields(logrus.Fields{
				"user_uuid":  userUUID,
				"start_date": startDate,
				"end_date":   endDate,
				"error":      err,
			}).Error("error scanning timeseries message row")
			return nil, err
		}
		timeseries = append(timeseries, ts)
	}

	if err = rows.Err(); err != nil {
		s.logger.WithFields(logrus.Fields{
			"user_uuid":  userUUID,
			"start_date": startDate,
			"end_date":   endDate,
			"error":      err,
		}).Error("error iterating timeseries message rows")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid":  userUUID,
		"start_date": startDate,
		"end_date":   endDate,
		"count":      len(timeseries),
	}).Info("timeseries messages retrieved successfully")

	return timeseries, nil
}

// Analytic - интерфейс для работы с аналитикой.
type Analytic interface {
	GetAverageLikes(userUUID uuid.UUID) (*AverageLikes, error)
	GetChatCounts(userUUID uuid.UUID) (*ChatCounts, error)
	GetDayCount(userUUID uuid.UUID) (*DayCount, error)
	GetFileCounts(userUUID uuid.UUID) (*FileCounts, error)
	GetMessageCounts(userUUID uuid.UUID) (*MessageCounts, error)
	GetTagCounts(userUUID uuid.UUID) ([]TagCount, error)
	GetTimeseriesMessages(userUUID uuid.UUID, startDate, endDate string) ([]TimeseriesMessage, error)
}
