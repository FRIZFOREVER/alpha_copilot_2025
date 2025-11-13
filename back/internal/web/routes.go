package web

import (
	"database/sql"
	"jabki/internal/client"
	"jabki/internal/web/handlers"
	"jabki/internal/web/middlewares"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/websocket/v2"
	"github.com/minio/minio-go"
	"github.com/sirupsen/logrus"
)

func InitServiceRoutes(server *fiber.App, db *sql.DB, secretServie string, logger *logrus.Logger) {
	history := handlers.NewHistory(db, logger)
	serviceAuthentication := middlewares.NewServiceAuthentication(secretServie, logger)
	server.Get("/historyForModel/:uuid/:chat_id", serviceAuthentication.Handler, history.Handler)
	server.Get(
		"/graph_log_writer/:chat_id",
		serviceAuthentication.Handler, func(c *fiber.Ctx) error {
			// Проверяем, является ли запрос WebSocket upgrade
			if websocket.IsWebSocketUpgrade(c) {
				c.Locals("allowed", true)
				return c.Next()
			}
			return fiber.ErrUpgradeRequired
		},
		handlers.GraphLogHandler(db, logger),
	)
}

func InitPublicRoutes(server *fiber.App, db *sql.DB, secretUser, frontOrigin string, logger *logrus.Logger) {
	server.Use(middlewares.Cors(frontOrigin))

	auth := handlers.NewAuth(db, secretUser, logger)
	server.Put("/auth", auth.Handler)

	reg := handlers.NewReg(db, secretUser, logger)
	server.Post("/reg", reg.Handler)
}

func InitJWTMiddleware(server *fiber.App, secret, frontOrigin string, logger *logrus.Logger) {
	userAuthentication := middlewares.NewUserAuthentication(secret, logger)
	server.Use(middlewares.Cors(frontOrigin), userAuthentication.Handler)
}

func InitPrivateRoutes(
	server *fiber.App,
	db *sql.DB,
	s3 *minio.Client,
	model *client.ModelClient,
	recognizer *client.RecognizerClient,
	streamClient *client.StreamMessageClient,
	logger *logrus.Logger,
) {
	message := handlers.NewMessage(model, db, logger)
	server.Post("/message/:chat_id", message.Handler)

	history := handlers.NewHistory(db, logger)
	server.Get("/history/:chat_id", history.Handler)

	clear := handlers.NewClear(db, logger)
	server.Delete("/clear/:chat_id", clear.Handler)

	like := handlers.NewLike(db, logger)
	server.Put("/like/:chat_id", like.Handler)

	voice := handlers.NewVoice(recognizer, s3, logger)
	server.Post("/voice", voice.Handler)

	proxy := handlers.NewProxy(s3, logger)
	server.Get("/voices/:file_name", proxy.HandlerWebm)
	server.Get("/files/:file_name", proxy.HandlerFile)

	chat := handlers.NewChat(db, logger)
	server.Post("/chat", chat.CreateHandler)
	server.Get("/chats", chat.GetHandler)
	server.Put("/chat/:chat_id", chat.RenameHandler)

	supportHistory := handlers.NewSupportHistory(db, logger)
	server.Get("/support_history/:chat_id", supportHistory.GetSupportsHistoryHandler)

	server.Use("/support", func(c *fiber.Ctx) error {
		// Проверяем, является ли запрос WebSocket upgrade
		if websocket.IsWebSocketUpgrade(c) {
			c.Locals("allowed", true)
			return c.Next()
		}
		return fiber.ErrUpgradeRequired
	})

	server.Get("/support/:chat_id", handlers.SupportHandler(db, logger))

	profile := handlers.NewProfile(db, logger)
	server.Get("/profile", profile.GetHandler)
	server.Put("/profile_other_info", profile.PutOtherInfoHandler)

	stream := handlers.NewStream(streamClient, db, streamClient.HistoryLen, logger)
	server.Post("/message_stream/:chat_id", stream.Handler)

	file := handlers.NewFile(s3, logger)
	server.Post("/file", file.Handler)

	server.Use("/graph_log", func(c *fiber.Ctx) error {
		// Проверяем, является ли запрос WebSocket upgrade
		if websocket.IsWebSocketUpgrade(c) {
			c.Locals("allowed", true)
			return c.Next()
		}
		return fiber.ErrUpgradeRequired
	})

	server.Get("/graph_log/:chat_id", handlers.GraphLogHandler(db, logger))

	search := handlers.NewSearch(db, logger)
	server.Get("/search", search.Handler)
}
