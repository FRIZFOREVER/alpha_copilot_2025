package handlers

import (
	"database/sql"
	"jabki/internal/client"

	"github.com/sirupsen/logrus"
)

type Stream struct {
	client *client.ModelClient
	db     *sql.DB
	logger *logrus.Logger
}

type streamIn struct{}
