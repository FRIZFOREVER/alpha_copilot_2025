package model

import "time"

type Message struct {
	QuestionID   int       `json:"question_id"`
	AnswerID     int       `json:"answer_id"`
	Question     string    `json:"question"`
	QuestionTag  *string   `json:"tag"`
	Answer       string    `json:"answer"`
	QuestionTime time.Time `json:"question_time"`
	AnswerTime   time.Time `json:"answer_time"`
	VoiceURL     string    `json:"voice_url"`
	FileURL      string    `json:"file_url"`
	Rating       *int      `json:"rating"`
}