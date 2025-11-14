package controller

import (
	"jabki/internal/middlewares"
	"jabki/internal/web/ws"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/websocket/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type Graph struct {
	service *service.Graph
	secret  string
	logger  *logrus.Logger
}

func NewGraph(service *service.Graph, secret string, logger *logrus.Logger) *Graph {
	return &Graph{
		service: service,
		secret:  secret,
		logger:  logger,
	}
}

func (gh *Graph) GraphLogHandler() fiber.Handler {
	return websocket.New(func(c *websocket.Conn) {
		var userUUID uuid.UUID
		var err error

		if gh.secret != "service" {
			userUUID, err = middlewares.RequestUserUUID(gh.secret, c.Query("jwt"), gh.logger)
			if err != nil {
				gh.logger.Errorf("Error processing JWT: %s", err)
				return
			}
		}

		uuidString := userUUID.String()
		chatID := c.Params("chat_id")

		ws.AddConnection(chatID, uuidString, c)
		defer ws.RemoveConnection(chatID, uuidString)

		gh.logger.Infof("WebSocket connection established for chat: %s, user: %s", chatID, uuidString)

		if err := c.WriteJSON(map[string]string{
			"type": "connection_established",
			"uuid": uuidString,
		}); err != nil {
			gh.logger.Error("Error sending JSON: ", err)
		}

		for {
			var msg ws.Message

			err := c.ReadJSON(&msg)
			if err != nil {
				gh.logger.Errorf("Error reading message: %v", err)
				break
			}

			gh.logger.Debugf("Chat %s | User %s: %s", chatID, uuidString, msg.Message)

			ws.BroadcastMessage(chatID, uuidString, msg)
		}
	})
}
