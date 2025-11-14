package model

type MessageHistory struct {
	ID      int    `json:"id"`
	Role    string `json:"role"`
	Content string `json:"content"`
}

// PayloadStream структура для входных данных.
type PayloadStream struct {
	Messages []MessageHistory `json:"messages"`
	ChatID   string           `json:"chat_id"`
	Tag      string           `json:"tag"`
	Mode     string           `json:"mode"`
	System   string           `json:"system"`
	FileURL  string           `json:"file_url"`
	IsVoice  bool             `json:"is_voice"`
}
