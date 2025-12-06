package internal

import (
	"context"
	"database/sql"
	"jabki/internal/client"
	"jabki/internal/database"
	"jabki/internal/s3"
	"jabki/internal/settings"
	"jabki/internal/web"
	"net/http"
	"time"

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
	db, err := database.InitDBWithPing(ctx, config.PostgresURL, logger)
	if err != nil {
		return nil, err
	}
	logger.Info("Есть подключение к БД postgres! 🐘")

	s3client, err := s3.InitMinioClient(config.S3URL, config.S3Login, config.S3Password, false)
	if err != nil {
		return nil, err
	}
	logger.Info("Есть подключение к S3 MINIO! 🐦")

	err = client.Ping(config.Model)
	if err != nil {
		logger.Fatalf("Нет подключение к api модели %v", err)
	}
	logger.Info("Есть подключение к api модели! ⚙️")

	// err = client.Ping(config.Recognizer)
	// if err != nil {
	// 	logger.Fatalf("Нет подключение к recognizer %v", err)
	// }
	// logger.Info("Есть подключение к recognizer! 🔊")

	// Проверка и логирование API ключа AssemblyAI
	if config.RecognizerAPIKey == "" {
		logger.Warn("⚠️  ASSEMBLYAI_API_KEY не установлен! Запросы к AssemblyAI будут возвращать ошибку 401")
		logger.Warn("   Установите переменную окружения ASSEMBLYAI_API_KEY в .env файле или docker-compose.yml")
	} else {
		// Маскируем ключ для безопасности (показываем только первые 8 символов)
		maskedKey := config.RecognizerAPIKey
		if len(maskedKey) > 8 {
			maskedKey = maskedKey[:8] + "..."
		}
		logger.Infof("AssemblyAI API ключ установлен: %s", maskedKey)
	}
	recognizerAssamblyAI := client.NewRecognizerClient("https://api.assemblyai.com/v2", "", config.RecognizerAPIKey, logger)
	recognizerWhisper := client.NewWhisperClient("POST", config.Recognizer, "/att", logger)
	streamClient := client.NewStreamMessageClient(http.MethodPost, config.Model, "/message_stream", config.HistoryLen, logger)

	web.InitServiceRoutes(server, db, config.SecretSerice, logger)
	web.InitPublicRoutes(server, db, config.SecretUser, config.FrontOrigin, logger)
	web.InitJWTMiddleware(server, config.SecretUser, config.FrontOrigin, logger)

	var isWisperServiceAlive *bool
	a := recognizerWhisper.Ping()
	isWisperServiceAlive = &a
	go func() {
		for {
			a = recognizerWhisper.Ping()
			isWisperServiceAlive = &a
			time.Sleep(4 * time.Second)
		}
	}()

	web.InitPrivateRoutes(
		server,
		db,
		s3client,
		recognizerAssamblyAI,
		config.RecognizerAPIKey != "",
		recognizerWhisper,
		isWisperServiceAlive,
		streamClient,
		config.Inteagrations,
		logger,
	)

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
