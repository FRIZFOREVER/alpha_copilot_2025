package web

import (
	"database/sql"
	"jabki/internal/client"
	"jabki/internal/database"
	"jabki/internal/s3"
	"jabki/internal/web/handlers"
	"jabki/internal/web/middlewares"

	"github.com/gofiber/fiber/v2"
	"github.com/minio/minio-go"
	"github.com/sirupsen/logrus"
)

func InitServiceRoutes(server fiber.Router, db *sql.DB, secretServie string, logger *logrus.Logger) {
	history := handlers.NewHistory(database.NewHistoryRepository(db, logger), logger)
	serviceAuthentication := middlewares.NewServiceAuthentication(secretServie, logger)
	server.Get("/historyForModel/:uuid/:chat_id", serviceAuthentication.Handler, history.Handler)
	graphLogRepo := database.NewGraphLogRepository(db, logger)
	server.Get("/graph_log_writer/:chat_id", middlewares.Upgrader, handlers.GraphLogHandlerWS("service", graphLogRepo, logger))
}

func InitPublicRoutes(server fiber.Router, db *sql.DB, secretUser, frontOrigin string, logger *logrus.Logger) {
	server.Use(middlewares.Cors(frontOrigin))

	authRepo := database.NewAuthService(db, logger)
	auth := handlers.NewAuth(authRepo, secretUser, logger)
	server.Put("/auth", auth.Handler)

	regRepo := database.NewRegistrationService(db, logger)
	reg := handlers.NewReg(regRepo, secretUser, logger)
	server.Post("/reg", reg.Handler)

	server.Use("/graph_log", middlewares.Upgrader)
	graphLogRepo := database.NewGraphLogRepository(db, logger)
	server.Get("/graph_log/:chat_id", handlers.GraphLogHandlerWS(secretUser, graphLogRepo, logger))
}

func InitJWTMiddleware(server fiber.Router, secret, frontOrigin string, logger *logrus.Logger) {
	userAuthentication := middlewares.NewUserAuthentication(secret, logger)
	server.Use(middlewares.Cors(frontOrigin), userAuthentication.Handler)
}

func InitPrivateRoutes(
	server fiber.Router,
	db *sql.DB,
	s3Client *minio.Client,
	recognizerAssambleAI *client.AssamblyAIClient,
	isAssamblyAIEnable bool,
	recognizerWhisper *client.WhisperClient,
	isWhisperAlive *bool,
	streamClient *client.StreamMessageClient,
	logger *logrus.Logger,
) {
	historyRepo := database.NewHistoryRepository(db, logger)
	history := handlers.NewHistory(historyRepo, logger)
	server.Get("/history/:chat_id", history.Handler)

	clear := handlers.NewClear(historyRepo, logger)
	server.Delete("/clear/:chat_id", clear.Handler)

	likeRepo := database.NewLikeRepository(db, logger)
	like := handlers.NewLike(likeRepo, logger)
	server.Put("/like/:chat_id", like.Handler)

	voiceStorage := s3.NewMinIOAudioFileManager(s3Client)
	voice := handlers.NewVoice(recognizerAssambleAI, recognizerWhisper, voiceStorage, isWhisperAlive, isAssamblyAIEnable, logger)
	server.Post("/voice", voice.Handler)

	fileStorege := s3.NewMinIOFileManager(s3Client)
	proxy := handlers.NewFileProxy(fileStorege, logger)
	server.Get("/files/:file_name", proxy.HandlerFile)

	audioStorage := s3.NewMinIOAudioFileManager(s3Client)
	proxyAudio := handlers.NewAudioProxy(audioStorage, logger)
	server.Get("/voices/:file_name", proxyAudio.HandlerWebm)

	chatRepo := database.NewChatRepository(db, logger)
	chat := handlers.NewChat(chatRepo, logger)
	server.Post("/chat", chat.CreateHandler)
	server.Get("/chats", chat.GetHandler)
	server.Put("/chat/:chat_id", chat.RenameHandler)

	profileRepo := database.NewProfileRepository(db, logger)
	profile := handlers.NewProfile(profileRepo, logger)
	server.Get("/profile", profile.GetHandler)
	server.Put("/profile_other_info", profile.PutOtherInfoHandler)

	streamRepo := database.NewMessageRepository(db, logger)
	stream := handlers.NewStream(streamClient, streamRepo, streamClient.HistoryLen, logger)
	server.Post("/message_stream/:chat_id", stream.Handler)

	file := handlers.NewFile(fileStorege, logger)
	server.Post("/file", file.Handler)

	searchRepo := database.NewSearchRepository(db, logger)
	search := handlers.NewSearch(searchRepo, logger)
	server.Get("/search", search.Handler)

	graphLogRepo := database.NewGraphLogRepository(db, logger)
	graphLog := handlers.NewGraphLog(graphLogRepo, logger)
	server.Get("/log/graph", graphLog.Handler)

	analyticRepo := database.NewAnalyticRepository(db, logger)
	analytic := handlers.NewAnalytic(analyticRepo, logger)
	analyticGroup := server.Group("/analytics")
	analyticGroup.Get("/average-likes", analytic.GetAverageLikesHandler)
	analyticGroup.Get("/chat-counts", analytic.GetChatCountsHandler)
	analyticGroup.Get("/day-count", analytic.GetDayCountHandler)
	analyticGroup.Get("/file-counts", analytic.GetFileCountsHandler)
	analyticGroup.Get("/message-counts", analytic.GetMessageCountsHandler)
	analyticGroup.Get("/tag-counts", analytic.GetTagCountsHandler)
	analyticGroup.Post("/timeseries-messages", analytic.GetTimeseriesMessagesHandler)
}
