package dto

type CreateChatIn struct {
	Name string `json:"name"`
}

type CreateChatOut struct {
	ChatID int `json:"chat_id"`
}