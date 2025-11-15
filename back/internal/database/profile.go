package database

import (
	"database/sql"
	_ "embed"

	"github.com/sirupsen/logrus"
)

//go:embed queries/get_profile.sql
var getProfileQuery string

//go:embed queries/update_other_users_info.sql
var updateOtherProfileInfo string

// Profile представляет структуру профиля пользователя.
type Profile struct {
	ID                     int     `json:"id"`
	Login                  string  `json:"login"`
	FIO                    string  `json:"username"`
	UserInfo               *string `json:"user_info"`
	BusinessInfo           *string `json:"business_info"`
	AdditionalInstructions *string `json:"additional_instructions"`
}

// ProfileService - структура для работы с профилями пользователей.
type ProfileService struct {
	db     *sql.DB
	logger *logrus.Logger
}

// NewProfileRepository - конструктор для ProfileService.
func NewProfileRepository(db *sql.DB, logger *logrus.Logger) *ProfileService {
	return &ProfileService{
		db:     db,
		logger: logger,
	}
}

// GetProfile - метод для получения профиля пользователя.
func (s *ProfileService) GetProfile(uuid string) (Profile, error) {
	var profile Profile

	err := s.db.QueryRow(getProfileQuery, uuid).Scan(
		&profile.ID,
		&profile.FIO,
		&profile.Login,
		&profile.UserInfo,
		&profile.BusinessInfo,
		&profile.AdditionalInstructions,
	)
	if err != nil {
		s.logger.WithError(err).Error("Failed to query profile")
		return profile, err
	}
	return profile, nil
}

// UpdateOtherProfileInfo - метод для обновления информации профиля.
func (s *ProfileService) UpdateOtherProfileInfo(
	uuid string,
	userInfo string,
	businessInfo string,
	additionalInstructions string,
) error {
	_, err := s.db.Exec(updateOtherProfileInfo, userInfo, businessInfo, additionalInstructions, uuid)
	if err != nil {
		s.logger.WithError(err).Error("Failed update other profile info")
		return err
	}
	return nil
}

// ProfileManager - интерфейс для управления профилями пользователей.
type ProfileManager interface {
	GetProfile(uuid string) (Profile, error)
	UpdateOtherProfileInfo(uuid string, userInfo string, businessInfo string, additionalInstructions string) error
}
