package database

import (
	"database/sql"
	_ "embed"

	"github.com/sirupsen/logrus"
)

//go:embed queries/get_profile.sql
var getProfileQuery string

func GetProfile(
	db *sql.DB,
	uuid string,
	logger *logrus.Logger,
) (
	profile Profile,
	err error,
) {
	err = db.QueryRow(getProfileQuery, uuid).Scan(&profile.ID, &profile.FIO, &profile.Login)
	if err != nil {
		logger.WithError(err).Error("Failed to query supports")
		return profile, err
	}
	return profile, nil
}

type Profile struct {
	ID    int    `json:"id"`
	Login string `json:"login"`
	FIO   string `json:"username"`
}
