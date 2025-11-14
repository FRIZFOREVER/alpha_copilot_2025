package database

import (
	"database/sql"
	_ "embed"
	"errors"
	"time"

	"github.com/sirupsen/logrus"
)

//go:embed queries/create_chat.sql
var createChatQuery string

//go:embed queries/get_chats.sql
var getChatsQuery string

//go:embed queries/check_chat.sql
var checkChatQuery string

//go:embed queries/rename_chat.sql
var renameChatQuery string

var ErrUserByUUIDNotFound = errors.New("user with this UUID not found")

// Chat представляет структуру чата.
type Chat struct {
	ChatID     int       `json:"chat_id"`
	Name       string    `json:"name"`
	CreateTime time.Time `json:"create_time"`
}

// ChatService - структура для работы с чатами.
type ChatService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewChatRepository - конструктор для ChatService.
func NewChatRepository(db *sql.DB, logger *logrus.Logger) *ChatService {
	return &ChatService{
		db:     db,
		logger: logger,
	}
}

// CreateChat - метод для создания нового чата.
func (s *ChatService) CreateChat(chatName string, userUUID string) (int, error) {
	var chatID int

	err := s.db.QueryRow(createChatQuery, chatName, userUUID).Scan(&chatID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			s.logger.WithFields(logrus.Fields{
				"chat_name": chatName,
				"user_uuid": userUUID,
				"error":     err,
			}).Warn("chat creation failed: user not found or other constraint violation")
			return 0, ErrUserByUUIDNotFound
		}

		s.logger.WithFields(logrus.Fields{
			"chat_name": chatName,
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during chat creation")
		return 0, err
	}

	s.logger.WithFields(logrus.Fields{
		"chat_name": chatName,
		"user_uuid": userUUID,
		"chat_id":   chatID,
	}).Info("chat created successfully")

	return chatID, nil
}

// GetChats - метод для получения списка чатов пользователя.
func (s *ChatService) GetChats(userUUID string) ([]Chat, error) {
	rows, err := s.db.Query(getChatsQuery, userUUID)
	if err != nil {
		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("database error during fetching chats")
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			s.logger.Error("Ошибка закрытия строк: ", err)
		}
	}()

	var chats []Chat
	for rows.Next() {
		var chat Chat
		err := rows.Scan(&chat.ChatID, &chat.Name, &chat.CreateTime)
		if err != nil {
			s.logger.WithFields(logrus.Fields{
				"user_uuid": userUUID,
				"error":     err,
			}).Error("error scanning chat row")
			return nil, err
		}
		chats = append(chats, chat)
	}

	if err = rows.Err(); err != nil {
		s.logger.WithFields(logrus.Fields{
			"user_uuid": userUUID,
			"error":     err,
		}).Error("error iterating chat rows")
		return nil, err
	}

	s.logger.WithFields(logrus.Fields{
		"user_uuid":  userUUID,
		"chat_count": len(chats),
	}).Info("chats fetched successfully")

	return chats, nil
}

// CheckChat - метод для проверки принадлежности чата пользователю.
func (s *ChatService) CheckChat(userUUID string, chatID int) (bool, error) {
	var isCorresponds bool

	err := s.db.QueryRow(checkChatQuery, userUUID, chatID).Scan(&isCorresponds)
	if err != nil {
		if err == sql.ErrNoRows {
			// Если запрос не вернул строк, считаем что чат не соответствует пользователю
			return false, nil
		}
		s.logger.WithError(err).Error("failed to check chat ownership")
		return false, err
	}

	return isCorresponds, nil
}

// RenameChat - метод для переименования чата.
func (s *ChatService) RenameChat(chatID int, newName string) error {
	_, err := s.db.Exec(renameChatQuery, chatID, newName)
	if err != nil {
		s.logger.WithError(err).Error("failed to rename chat")
	}

	return err
}

// ChatManager - единый интерфейс для управления чатами.
type ChatManager interface {
	CreateChat(chatName string, userUUID string) (int, error)
	GetChats(userUUID string) ([]Chat, error)
	CheckChat(userUUID string, chatID int) (bool, error)
	RenameChat(chatID int, newName string) error
}
