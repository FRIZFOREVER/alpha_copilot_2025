package handlers

import (
	"jabki/internal/database"
	"jabki/internal/web/middlewares"
	"jabki/internal/web/ws"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/websocket/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type GraphLog struct {
	repo   database.GraphLogRepository
	logger *logrus.Logger
}

func NewGraphLog(repo database.GraphLogRepository, logger *logrus.Logger) *GraphLog {
	return &GraphLog{
		repo:   repo,
		logger: logger,
	}
}

func (gh *GraphLog) Handler(c *fiber.Ctx) error {
	answerIDStr := c.Query("answer_id")
	if answerIDStr == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "answer_id is a required query parameter",
		})
	}

	answerID, err := strconv.Atoi(answerIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid answer ID format",
		})
	}

	graphLog, err := gh.repo.GetGraphLog(answerID)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error":   "Error get user profile",
			"details": err.Error(),
		})
	}

	return c.Status(fiber.StatusCreated).JSON(graphLog)
}

func GraphLogHandlerWS(secret string, repo database.GraphLogRepository, logger *logrus.Logger) fiber.Handler {
	return websocket.New(func(c *websocket.Conn) {
		var uuid uuid.UUID
		var err error
		if secret != "service" {
			uuid, err = middlewares.RequestUserUUID(secret, c.Query("jwt"), logger)
			if err != nil {
				logger.Errorf("Error Ошибка при обработки JWT error!!!: %s", err)
				return
			}
		}

		userUUID := uuid.String()
		// Получаем chat_id из параметров пути
		chatID := c.Params("chat_id")

		// Добавляем соединение в хранилище
		ws.AddConnection(chatID, userUUID, c)
		defer ws.RemoveConnection(chatID, userUUID)

		logger.Infof("WebSocket соединение установлено для чата: %s, пользователь: %s (UUID: %s)\n", chatID, userUUID, userUUID)

		// Отправляем пользователю подтверждение подключения
		if err := c.WriteJSON(map[string]string{
			"type": "connection_established",
			"uuid": userUUID,
		}); err != nil {
			logger.Error("Ошибка отправки json: ", err)
		}

		for {
			var msg ws.Message

			// Читаем сообщение от клиента
			err := c.ReadJSON(&msg)
			if err != nil {
				logger.Errorf("Ошибка чтения сообщения: %v\n", err)
				break
			}

			if err := repo.UpdateGraphLog(msg.Message, msg.Tag, msg.AnswerID); err != nil {
				logger.Errorf("Ошибка записи данных в бд: ", err.Error())
			}
			// Выводим сообщение в консоль
			logger.Infof("Получено graph_log сообщение: Чат %s | Пользователь %s | Tag: %s | AnswerID: %d | Message: %s\n", chatID, userUUID, msg.Tag, msg.AnswerID, msg.Message)

			// Отправляем сообщение всем пользователям в чате, кроме отправителя
			logger.Infof("Трансляция сообщения в чат %s, отправитель UUID: %s\n", chatID, userUUID)
			ws.BroadcastMessage(chatID, userUUID, msg)
		}
	})
}
