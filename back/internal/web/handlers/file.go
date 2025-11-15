package handlers

import (
	"io"
	"jabki/internal/s3"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

type File struct {
	storage s3.FileManager
	logger  *logrus.Logger
}

func NewFile(storage s3.FileManager, logger *logrus.Logger) *File {
	return &File{
		storage: storage,
		logger:  logger,
	}
}

func (fh *File) Handler(c *fiber.Ctx) error {
	uuid := c.Locals("uuid").(uuid.UUID)
	var fileOut fileOut
	var err error

	// Получаем файл из формы
	file, err := c.FormFile("file")
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Не удалось получить файл: " + err.Error(),
		})
	}

	// Открываем загруженный файл
	uploadedFile, err := file.Open()
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Не удалось открыть файл: " + err.Error(),
		})
	}
	defer func() {
		if err := uploadedFile.Close(); err != nil {
			fh.logger.Error("Error close file: ", err)
		}
	}()

	// Читаем содержимое файла в байты
	fileBytes, err := io.ReadAll(uploadedFile)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Не удалось прочитать файл: " + err.Error(),
		})
	}

	// Получаем расширение файла
	fileExt := strings.ToLower(filepath.Ext(file.Filename))
	if fileExt == "" {
		fileExt = ".bin" // расширение по умолчанию для бинарных файлов
	}

	// Загружаем файл в S3
	url, err := fh.storage.UploadFile("files", uuid.String(), fileExt, fileBytes, file.Header.Get("Content-Type"))
	if err != nil {
		fh.logger.WithError(err).Error("Failed to upload file to S3")
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Не удалось загрузить файл в хранилище",
			"details": err.Error(),
		})
	}

	fileOut.FileURL = url

	return c.JSON(fileOut)
}

type fileOut struct {
	FileURL string `json:"file_url"`
}
