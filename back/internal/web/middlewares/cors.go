package middlewares

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
)

func Cors(allowOrigins string) fiber.Handler {
	return cors.New(cors.Config{
		AllowOrigins:     "*",                                           // Разрешенные источники
		AllowMethods:     "GET,POST,PUT,DELETE,OPTIONS",                 // Разрешенные методы (добавлен OPTIONS для preflight)
		AllowHeaders:     "Origin, Content-Type, Accept, Authorization", // Разрешенные заголовки
		AllowCredentials: true,
	})
}
