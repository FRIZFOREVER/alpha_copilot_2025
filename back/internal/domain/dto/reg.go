package dto

type RegIn struct {
	FIO      string `json:"username"`
	Login    string `json:"login"`
	Password string `json:"password"`
}

type RegOut struct {
	Jwt string `json:"jwt"`
}