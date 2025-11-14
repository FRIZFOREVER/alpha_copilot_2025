package dto

import "time"

type StreamIn struct {
	Question string `json:"question"`
	VoiceURL string `json:"voice_url"`
	FileURL  string `json:"file_url"`
	Tag      string `json:"tag"`
	Mode     string `json:"mode"`
}

type StreamMetaOut struct {
	QuestionID   int       `json:"question_id"`
	AnswerID     int       `json:"answer_id"`
	QuestionTime time.Time `json:"question_time"`
	Tag          string    `json:"tag"`
}

type StreamChunckOut struct {
	Content string    `json:"content"`
	Time    time.Time `json:"time"`
	Done    bool      `json:"done"`
}