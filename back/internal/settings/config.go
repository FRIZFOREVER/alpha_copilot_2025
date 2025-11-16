package settings

import (
	"github.com/joho/godotenv"
	"github.com/kelseyhightower/envconfig"
	"github.com/sirupsen/logrus"
)

type Settings struct {
	Port         string `envconfig:"PORT"                 default:":8080"`
	Debug        string `envconfig:"DEBUG"                default:"INFO"`
	SecretSerice string `envconfig:"SECRET_SERVICE"       default:"secret_service"`
	SecretUser   string `envconfig:"SECRET_USER"          default:"secret_user"`

	PostgresURL string `envconfig:"POSTGRES_URL"          default:"postgres://app:app123@postgres:5432/app?sslmode=disable"`

	S3URL        string `envconfig:"S3_URL"               default:"minio:9000"`
	S3BacketName string `envconfig:"S3_BACKET_NAME"       default:"voices"`
	S3Login      string `envconfig:"S3_LOGIN"             default:"minio-user"`
	S3Password   string `envconfig:"S3_PASSWORD"          default:"minio-password"`

	Model      string `envconfig:"MODEL"                       default:"http://ml-api:8000"`
	HistoryLen int    `envconfig:"HISTORY_LEN"                 default:"5"`

	Recognizer       string `envconfig:"RECOGNIZER"       default:"http://recognizer-service:3333"`
	RecognizerAPIKey string `envconfig:"ASSEMBLYAI_API_KEY"`

	FrontOrigin string `envconfig:"FRONT_ORIGIB"    default:"http://localhost:5173"`
}

func InitSettings(logger *logrus.Logger) Settings {
	var settings Settings
	if err := godotenv.Load("back.env"); err != nil {
		logger.Warn("godotenv:  Error loading .env file", err)
	}

	if err := envconfig.Process("", &settings); err != nil {
		logger.Error("envconfig: Error loading environment variables", err)
	}

	return settings
}
