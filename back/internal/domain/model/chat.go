package model

import "time"

type Chat struct {
	ChatID     int       `json:"chat_id"`
	Name       string    `json:"name"`
	CreateTime time.Time `json:"create_time"`
}