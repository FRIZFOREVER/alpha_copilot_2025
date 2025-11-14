package main

import (
	"jabki/internal"
	"jabki/internal/settings"

	"github.com/sirupsen/logrus"
)

func main() {
	logger := logrus.New()
	logger.SetLevel(logrus.DebugLevel)
	settings := settings.InitSettings(logger)
	app, err := internal.InitApp(&settings, logger)
	if err != nil {
		if err := app.Stop(); err != nil {
			logger.Error("Ошибка при остановке приложения")
		}
		logger.Fatal("Ошибка инициализации проекта: ", err)
	}
	defer func() {
		if err := app.Stop(); err != nil {
			logger.Error("Ошибка при остановке приложения")
		}
	}()
	logger.Fatal(app.Start())
}
