package handlers

import (
	"errors"
	"fmt"
	"io"
	"jabki/internal/s3"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
)

var (
	ErrFileIsNotAnAudioMpegFile = errors.New("file is not an audio/mpeg file")
	ErrInvalidFilePath          = errors.New("invalid file path format")
)

type FileProxy struct {
	fileManager s3.FileManager
	logger      *logrus.Logger
}

func NewFileProxy(fileManager s3.FileManager, logger *logrus.Logger) *FileProxy {
	return &FileProxy{
		fileManager: fileManager,
		logger:      logger,
	}
}

func (fp *FileProxy) HandlerFile(c *fiber.Ctx) error {
	fileName := c.Params("file_name")
	bucket := "files"

	object, err := fp.fileManager.GetFile(bucket, fileName)
	if err != nil {
		fp.logger.WithError(err).Errorf("Failed to get file from S3: bucket=%s, file=%s", bucket, fileName)
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
			"error": "File not found",
		})
	}
	defer func() {
		if err := object.Close(); err != nil {
			fp.logger.Error("Error close s3 object", err)
		}
	}()

	// Получаем информацию о файле для определения Content-Type
	objectInfo, err := object.Stat()
	if err != nil {
		fp.logger.WithError(err).Errorf("Failed to get file stats: bucket=%s, file=%s", bucket, fileName)
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to get file information",
		})
	}

	// Определяем Content-Type и настройки отдачи
	contentType, disposition := getContentDisposition(objectInfo.ContentType, fileName)

	c.Set("Content-Type", contentType)
	c.Set("Content-Disposition", disposition)
	c.Set("Cache-Control", "public, max-age=3600")
	c.Set("Content-Length", fmt.Sprintf("%d", objectInfo.Size))

	// Потоковая передача файла
	_, err = io.Copy(c.Response().BodyWriter(), object)
	if err != nil {
		fp.logger.WithError(err).Error("Failed to stream file")
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to stream file",
		})
	}

	return nil
}

// getContentDisposition определяет Content-Type и Content-Disposition.
func getContentDisposition(contentType, fileName string) (string, string) {
	// Если Content-Type не определен, пытаемся определить по расширению
	if contentType == "" || contentType == "application/octet-stream" {
		contentType = getContentTypeByExtension(filepath.Ext(fileName))
	}

	// Для безопасных типов контента используем inline, для остальных - attachment
	switch {
	case strings.HasPrefix(contentType, "image/"),
		strings.HasPrefix(contentType, "video/"),
		strings.HasPrefix(contentType, "audio/"),
		strings.HasPrefix(contentType, "text/"),
		contentType == "application/pdf":
		return contentType, fmt.Sprintf("inline; filename=\"%s\"", fileName)
	default:
		return contentType, fmt.Sprintf("attachment; filename=\"%s\"", fileName)
	}
}

// getContentTypeByExtension определяет Content-Type по расширению файла.
func getContentTypeByExtension(ext string) string {
	switch strings.ToLower(ext) {
	case ".pdf":
		return "application/pdf"
	case ".jpg", ".jpeg":
		return "image/jpeg"
	case ".png":
		return "image/png"
	case ".gif":
		return "image/gif"
	case ".txt":
		return "text/plain"
	case ".html", ".htm":
		return "text/html"
	case ".json":
		return "application/json"
	case ".mp3":
		return "audio/mpeg"
	case ".webm":
		return "audio/webm"
	case ".mp4":
		return "video/mp4"
	case ".zip":
		return "application/zip"
	case ".doc":
		return "application/msword"
	case ".docx":
		return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
	case ".xls":
		return "application/vnd.ms-excel"
	case ".xlsx":
		return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
	case ".ppt":
		return "application/vnd.ms-powerpoint"
	case ".pptx":
		return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
	default:
		return "application/octet-stream"
	}
}

type AudioProxy struct {
	audioManager s3.AudioFileManager
	logger       *logrus.Logger
}

func NewAudioProxy(audioManager s3.AudioFileManager, logger *logrus.Logger) *AudioProxy {
	return &AudioProxy{
		audioManager: audioManager,
		logger:       logger,
	}
}

func (ap *AudioProxy) HandlerWebm(c *fiber.Ctx) error {
	fileName := c.Params("file_name")

	// Проверяем что файл имеет расширение .webm
	if !strings.HasSuffix(fileName, ".webm") {
		fileName += ".webm"
	}

	bucket := "voices"

	object, err := ap.audioManager.Get(bucket, fileName)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": err.Error(),
		})
	}
	defer func() {
		if err := object.Close(); err != nil {
			ap.logger.Error("Error close s3 object", err)
		}
	}()

	c.Set("Content-Type", "audio/mpeg")
	c.Set("Content-Disposition", fmt.Sprintf("inline; filename=\"%s\"", fileName))
	c.Set("Cache-Control", "public, max-age=3600")

	_, err = io.Copy(c.Response().BodyWriter(), object)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": fmt.Sprintf("Failed to stream file: %v", err),
		})
	}

	return nil
}
