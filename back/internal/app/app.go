package app

import (
	"context"
	"database/sql"
	client "jabki/internal/client/http"
	postgres "jabki/internal/repository/postrges"
	s3 "jabki/internal/s3/minio"
	"jabki/internal/settings"
	"net/http"

	"github.com/gofiber/fiber/v2"
	"github.com/minio/minio-go"
	"github.com/sirupsen/logrus"
)

type App struct {
	Config *settings.Settings
	Server *fiber.App
	DB     *sql.DB
	S3     *minio.Client
	logger *logrus.Logger
}

func InitApp(config *settings.Settings, logger *logrus.Logger) (*App, error) {
	ctx := context.Background()
	server := fiber.New(fiber.Config{
		// Устанавливаем лимит тела запроса до 101 МБ (для запаса)
		BodyLimit: 101 * 1024 * 1024,
	})

	var err error
	db, err := postgres.InitDBWithPing(ctx, config.PostgresURL, logger)
	if err != nil {
		return nil, err
	}
	logger.Info("Есть подключение к БД postgres! 🐘")

	s3client, err := s3.InitMinioClient(config.S3URL, config.S3Login, config.S3Password, false)
	if err != nil {
		return nil, err
	}
	logger.Info("Есть подключение к S3 MINIO! 🐦")

	// Проверка и логирование API ключа AssemblyAI
	if config.RecognizerAPIKey == "" {
		logger.Warn("⚠️  ASSEMBLYAI_API_KEY не установлен! Запросы к AssemblyAI будут возвращать ошибку 401")
		logger.Warn("   Установите переменную окружения ASSEMBLYAI_API_KEY в .env файле или docker-compose.yml")
	} else {
		logger.Infof("AssemblyAI API ключ установлен!")
	}
	recognizerClient := client.NewRecognizerClient("https://api.assemblyai.com/v2", "", config.RecognizerAPIKey, logger)
	streamClient := client.NewStreamClient(http.MethodPost, config.Model, "/message_stream", config.HistoryLen, logger)

	err = streamClient.Ping()
	if err != nil {
		logger.Fatalf("Нет подключение к api модели %v", err)
	}
	logger.Info("Есть подключение к api модели! ⚙️")

	initServiceRoutes(server, db, config.SecretSerice, logger)
	initPublicRoutes(server, db, config.SecretUser, config.FrontOrigin, logger)
	initJWTMiddleware(server, config.SecretUser, config.FrontOrigin, logger)
	initPrivateRoutes(server, db, s3client, streamClient, recognizerClient, logger)

	return newApp(config, server, db, s3client, logger), nil
}

func newApp(
	config *settings.Settings,
	server *fiber.App,
	db *sql.DB,
	s3 *minio.Client,
	logger *logrus.Logger,
) *App {
	return &App{
		Config: config,
		Server: server,
		DB:     db,
		S3:     s3,
		logger: logger,
	}
}

func (a *App) Start() error {
	return a.Server.Listen(a.Config.Port)
}

func (a *App) Stop() error {
	if a == nil {
		return nil
	}
	err := a.DB.Close()
	return err
}
