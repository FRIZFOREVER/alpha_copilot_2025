package s3

import (
	"bytes"
	"errors"
	"fmt"
	"time"

	"github.com/minio/minio-go"
)

var (
	ErrFilenameIsRequired           = errors.New("filename is required")
	ErrFailedToCheckBucketExistence = errors.New("failed to check bucket existence")
	ErrBucketNotFound               = errors.New("bucket not found")
	ErrFileNotFound                 = errors.New("file not found")
	ErrFailedToGetFileInfo          = errors.New("failed to get file info")
	ErrFileIsNotAnAudioMpegFile     = errors.New("file is not an audio/mpeg file")
)

// MinIOAudioFileManager реализует интерфейс AudioFileManager для работы с MinIO.
type MinIOAudioFileManager struct {
	client *minio.Client
}

// NewMinIOAudioFileManager создает новый экземпляр MinIOAudioFileManager.
func NewMinIOAudioFileManager(client *minio.Client) *MinIOAudioFileManager {
	return &MinIOAudioFileManager{
		client: client,
	}
}

// Upload загружает WEBM файл в объектное хранилище
// Возвращает путь к файлу или ошибку в случае неудачи.
func (m *MinIOAudioFileManager) Upload(bucketName, uuid string, mp3Data []byte) (string, error) {
	fileName := fmt.Sprintf("%s_%d.webm", uuid, time.Now().Unix())

	reader := bytes.NewReader(mp3Data)

	info, err := m.client.PutObject(bucketName, fileName, reader, int64(len(mp3Data)), minio.PutObjectOptions{
		ContentType: "audio/mpeg",
	})
	if err != nil {
		return "", fmt.Errorf("ошибка загрузки файла в MinIO: %w", err)
	}

	if info == 0 {
		return "", fmt.Errorf("файл не был загружен, размер 0")
	}

	return fmt.Sprintf("/%s/%s", bucketName, fileName), nil
}

// Get получает WEBM файл из объектного хранилища
// Возвращает объект файла или ошибку, если файл не найден или не является WEBM.
func (m *MinIOAudioFileManager) Get(bucket, fileName string) (File, error) {
	if fileName == "" {
		return nil, ErrFilenameIsRequired
	}

	// Проверяем существование бакета
	exists, err := m.client.BucketExists(bucket)
	if err != nil {
		return nil, fmt.Errorf("%w: %w", ErrFailedToCheckBucketExistence, err)
	}
	if !exists {
		return nil, ErrBucketNotFound
	}

	// Получаем объект из MinIO
	object, err := m.client.GetObject(bucket, fileName, minio.GetObjectOptions{})
	if err != nil {
		return nil, fmt.Errorf("%w: %w", ErrFileNotFound, err)
	}

	// Получаем информацию об объекте
	objectInfo, err := object.Stat()
	if err != nil {
		return nil, fmt.Errorf("%w: %w", ErrFailedToGetFileInfo, err)
	}

	// Проверяем, что файл имеет audio/mpeg тип
	if objectInfo.ContentType != "audio/mpeg" {
		return nil, ErrFileIsNotAnAudioMpegFile
	}

	return object, nil
}
