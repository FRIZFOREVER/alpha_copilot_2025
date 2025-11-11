package s3

import (
	"bytes"
	"fmt"
	"time"

	"github.com/minio/minio-go"
)

// MaxFileSize определяет максимальный размер файла (100 МБ в байтах)
const MaxFileSize = 100 * 1024 * 1024 // 100 МБ

// UploadFileToMinIO загружает любой файл в MinIO с проверкой размера
func UploadFileToMinIO(s3 *minio.Client, bucketName, uuid, fileExtension string, fileData []byte, contentType string) (string, error) {
	// Проверяем размер файла
	fileSize := int64(len(fileData))
	if fileSize > MaxFileSize {
		return "", fmt.Errorf("размер файла превышает максимально допустимый: %d байт > %d байт", fileSize, MaxFileSize)
	}

	if fileSize == 0 {
		return "", fmt.Errorf("файл пустой")
	}

	// Генерируем имя файла с временной меткой и оригинальным расширением
	fileName := fmt.Sprintf("%s_%d%s", uuid, time.Now().Unix(), fileExtension)

	reader := bytes.NewReader(fileData)

	// Если ContentType не указан, определяем по расширению или используем общий тип
	if contentType == "" {
		contentType = getContentTypeByExtension(fileExtension)
	}

	info, err := s3.PutObject(bucketName, fileName, reader, fileSize, minio.PutObjectOptions{
		ContentType: contentType,
	})
	if err != nil {
		return "", fmt.Errorf("ошибка загрузки файла в MinIO: %w", err)
	}

	if info == 0 {
		return "", fmt.Errorf("файл не был загружен, размер 0")
	}

	return fmt.Sprintf("/%s/%s", bucketName, fileName), nil
}

// GetFile получает любой файл из MinIO
func GetFile(s3 *minio.Client, bucket, fileName string) (*minio.Object, error) {
	if fileName == "" {
		return nil, ErrFilenameIsRequired
	}

	// Проверяем существование бакета
	exists, err := s3.BucketExists(bucket)
	if err != nil {
		return nil, ErrFailedToCheckBucketExistence
	}
	if !exists {
		return nil, ErrBucketNotFound
	}

	// Получаем объект из MinIO
	object, err := s3.GetObject(bucket, fileName, minio.GetObjectOptions{})
	if err != nil {
		return nil, ErrFileNotFound
	}

	// Получаем информацию об объекте
	objectInfo, err := object.Stat()
	if err != nil {
		return nil, ErrFailedToGetFileInfo
	}

	// Проверяем размер файла (опционально)
	if objectInfo.Size > MaxFileSize {
		return nil, fmt.Errorf("размер файла превышает максимально допустимый")
	}

	return object, nil
}

// ValidateFileSize проверяет размер файла перед загрузкой
func ValidateFileSize(fileData []byte) error {
	fileSize := int64(len(fileData))
	if fileSize > MaxFileSize {
		return fmt.Errorf("размер файла превышает максимально допустимый: %d байт > %d байт", fileSize, MaxFileSize)
	}
	if fileSize == 0 {
		return fmt.Errorf("файл пустой")
	}
	return nil
}

// GetMaxFileSize возвращает максимальный разрешенный размер файла
func GetMaxFileSize() int64 {
	return MaxFileSize
}

// getContentTypeByExtension определяет Content-Type по расширению файла
func getContentTypeByExtension(ext string) string {
	switch ext {
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
	case ".html":
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
	default:
		return "application/octet-stream"
	}
}