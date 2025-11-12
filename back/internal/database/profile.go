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

func GetProfile(
	db *sql.DB,
	uuid string,
	logger *logrus.Logger,
) (
	profile Profile,
	err error,
) {
	err = db.QueryRow(getProfileQuery, uuid).Scan(&profile.ID, &profile.FIO, &profile.Login, &profile.UserInfo, &profile.BusinessInfo, &profile.AdditionalInstructions)
	if err != nil {
		logger.WithError(err).Error("Failed to query supports")
		return profile, err
	}
	return profile, nil
}

type Profile struct {
	ID                     int    `json:"id"`
	Login                  string `json:"login"`
	FIO                    string `json:"username"`
	UserInfo               *string `json:"user_info"`
	BusinessInfo           *string `json:"business_info"`
	AdditionalInstructions *string `json:"additional_instructions"`
}

func UpdateOtherProfileInfo(
	db *sql.DB,
	uuid string,
	UserInfo string,
	BusinessInfo string,
	AdditionalInstructions string,
	logger *logrus.Logger,
) (
	err error,
) {
	_, err = db.Exec(updateOtherProfileInfo, UserInfo, BusinessInfo, AdditionalInstructions, uuid)
	if err != nil {
		logger.WithError(err).Error("Failed update other profile info")
		return err
	}
	return nil
}
