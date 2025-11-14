package postgres

import (
	"database/sql"
	_ "embed"
	"jabki/internal/domain/model"

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
	profile model.Profile,
	err error,
) {
	err = db.QueryRow(getProfileQuery, uuid).Scan(&profile.ID, &profile.FIO, &profile.Login, &profile.UserInfo, &profile.BusinessInfo, &profile.AdditionalInstructions)
	if err != nil {
		logger.WithError(err).Error("Failed to query supports")
		return profile, err
	}
	return profile, nil
}

func UpdateOtherProfileInfo(
	db *sql.DB,
	uuid string,
	userInfo string,
	businessInfo string,
	additionalInstructions string,
	logger *logrus.Logger,
) (
	err error,
) {
	_, err = db.Exec(updateOtherProfileInfo, userInfo, businessInfo, additionalInstructions, uuid)
	if err != nil {
		logger.WithError(err).Error("Failed update other profile info")
		return err
	}
	return nil
}
