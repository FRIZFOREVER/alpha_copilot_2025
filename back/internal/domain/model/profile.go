package model

type Profile struct {
	ID                     int     `json:"id"`
	Login                  string  `json:"login"`
	FIO                    string  `json:"username"`
	UserInfo               *string `json:"user_info"`
	BusinessInfo           *string `json:"business_info"`
	AdditionalInstructions *string `json:"additional_instructions"`
}