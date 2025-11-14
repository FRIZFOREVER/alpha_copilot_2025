package model

import "time"

type Support struct {
	ID         int       `json:"id"`
	Message    string    `json:"message"`
	UserUUID   string    `json:"user_uuid"`
	ChatID     int       `json:"chat_id"`
	CreateDate time.Time `json:"create_date"`
}