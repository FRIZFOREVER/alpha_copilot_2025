package app

import (
	"database/sql"
	client "jabki/internal/client/http"
	"jabki/internal/controller"
	"jabki/internal/middlewares"

	"github.com/gofiber/fiber/v2"
	"github.com/minio/minio-go"
	"github.com/sirupsen/logrus"
)

func initServiceRoutes(server *fiber.App, db *sql.DB, secretServie string, logger *logrus.Logger) {
	history := controller.NewHistory(db, logger)
	serviceAuthentication := middlewares.NewServiceAuthentication(secretServie, logger)
	server.Get("/historyForModel/:uuid/:chat_id", serviceAuthentication.Handler, history.Handler)
	server.Get(
		"/graph_log_writer/:chat_id",
		middlewares.UpgradeWS,
		controller.GraphLogHandler(db, "service", logger),
	)
}

func initPublicRoutes(server *fiber.App, db *sql.DB, secretUser, frontOrigin string, logger *logrus.Logger) {
	server.Use(middlewares.Cors(frontOrigin))

	auth := controller.NewAuth(db, secretUser, logger)
	server.Put("/auth", auth.Handler)

	reg := controller.NewReg(db, secretUser, logger)
	server.Post("/reg", reg.Handler)

	server.Use("/graph_log", middlewares.UpgradeWS)

	graph := controller.NewGraph(db, secretUser, logger)
	server.Get("/graph_log/:chat_id", graph.GraphLogHandler)
}

func initJWTMiddleware(server *fiber.App, secret, frontOrigin string, logger *logrus.Logger) {
	userAuthentication := middlewares.NewUserAuthentication(secret, logger)
	server.Use(middlewares.Cors(frontOrigin), userAuthentication.Handler)
}

func initPrivateRoutes(
	server *fiber.App,
	db *sql.DB,
	s3 *minio.Client,
	streamClient *client.StreamClient,
	recognizer *client.RecognizerClient,
	logger *logrus.Logger,
) {

	history := controller.NewHistory(db, logger)
	server.Get("/history/:chat_id", history.Handler)

	clear := controller.NewClear(db, logger)
	server.Delete("/clear/:chat_id", clear.Handler)

	like := controller.NewLike(db, logger)
	server.Put("/like/:chat_id", like.Handler)

	voice := controller.NewVoice(recognizer, s3, logger)
	server.Post("/voice", voice.Handler)

	proxy := controller.NewProxy(s3, logger)
	server.Get("/voices/:file_name", proxy.HandlerWebm)
	server.Get("/files/:file_name", proxy.HandlerFile)

	chat := controller.NewChat(db, logger)
	server.Post("/chat", chat.CreateHandler)
	server.Get("/chats", chat.GetHandler)
	server.Put("/chat/:chat_id", chat.RenameHandler)

	supportHistory := controller.NewSupportHistory(db, logger)
	server.Get("/support_history/:chat_id", supportHistory.GetSupportsHistoryHandler)

	server.Use("/support", middlewares.UpgradeWS)

	server.Get("/support/:chat_id", controller.SupportHandler(db, logger))

	profile := controller.NewProfile(db, logger)
	server.Get("/profile", profile.GetHandler)
	server.Put("/profile_other_info", profile.PutOtherInfoHandler)

	stream := controller.NewStream(streamClient, db, streamClient.HistoryLen, logger)
	server.Post("/message_stream/:chat_id", stream.Handler)

	file := controller.NewFile(s3, logger)
	server.Post("/file", file.Handler)

	search := controller.NewSearch(db, logger)
	server.Get("/search", search.Handler)
}
