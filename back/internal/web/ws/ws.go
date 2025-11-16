package ws

import (
	"fmt"
	"sync"

	"github.com/gofiber/websocket/v2"
)

type Message struct {
	Tag      string `json:"tag"`
	AnswerID int    `json:"answer_id"`
	Message  string `json:"message"`
}

// Структура для хранения информации о соединении.
type ConnectionInfo struct {
	Conn *websocket.Conn
	UUID string
}

// Изменяем структуру хранения соединений.
var (
	Connections = make(map[string]map[string]*ConnectionInfo) // chatID -> userUUID -> ConnectionInfo
	mu          sync.RWMutex
)

// Функция для отправки сообщения всем пользователям в чате, кроме отправителя.
func BroadcastMessage(chatID, senderUUID string, message Message) {
	mu.RLock()
	defer mu.RUnlock()

	chatConnections, exists := Connections[chatID]
	if !exists {
		return
	}

	for userUUID, connInfo := range chatConnections {
		if userUUID == senderUUID {
			continue
		}

		err := connInfo.Conn.WriteJSON(message)
		if err != nil {
			fmt.Printf("Ошибка отправки сообщения пользователю %s: %v\n", userUUID, err)
		} else {
			fmt.Printf("BroadcastMessage: Сообщение успешно отправлено пользователю %s\n", userUUID)
		}
	}
}

// Функция для добавления соединения.
func AddConnection(chatID, userUUID string, conn *websocket.Conn) {
	mu.Lock()
	defer mu.Unlock()

	if Connections[chatID] == nil {
		Connections[chatID] = make(map[string]*ConnectionInfo)
	}

	Connections[chatID][userUUID] = &ConnectionInfo{
		Conn: conn,
		UUID: userUUID,
	}
}

// Функция для удаления соединения.
func RemoveConnection(chatID, userUUID string) {
	mu.Lock()
	defer mu.Unlock()

	if chatConnections, exists := Connections[chatID]; exists {
		delete(chatConnections, userUUID)

		// Если в чате не осталось пользователей, удаляем чат
		if len(chatConnections) == 0 {
			delete(Connections, chatID)
		}
	}
}
