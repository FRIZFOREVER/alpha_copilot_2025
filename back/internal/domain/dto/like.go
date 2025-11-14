package dto

type LikeIn struct {
	AnswerID int  `json:"answer_id"`
	Rating   *int `json:"rating"`
}