package handlers

import (
	"database/sql"
	"jabki/internal/web/middlewares"
	"jabki/internal/web/ws"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/websocket/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

func GraphLogHandler(db *sql.DB, secret string, logger *logrus.Logger) fiber.Handler {
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

		logger.Infof("WebSocket соединение установлено для чата: %s, пользователь: %s\n", chatID, userUUID)

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

			// Выводим сообщение в консоль
			logger.Debugf("Чат %s | Пользователь %s: %s\n", chatID, userUUID, msg.Message)

			// Отправляем сообщение всем пользователям в чате, кроме отправителя
			ws.BroadcastMessage(chatID, userUUID, msg)
		}
	})
}
