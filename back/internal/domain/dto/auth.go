package dto

type AuthIn struct {
	Login    string `json:"login"`
	Password string `json:"password"`
}

type AuthOut struct {
	Jwt string `json:"jwt"`
}