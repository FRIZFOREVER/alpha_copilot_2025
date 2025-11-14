package minio

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

func UploadMP3ToMinIO(s3 *minio.Client, bucketName, uuid string, mp3Data []byte) (string, error) {
	fileName := fmt.Sprintf("%s_%d.webm", uuid, time.Now().Unix())

	reader := bytes.NewReader(mp3Data)

	info, err := s3.PutObject(bucketName, fileName, reader, int64(len(mp3Data)), minio.PutObjectOptions{
		ContentType: "audio/mpeg",
	})
	if err != nil {
		// TODO обернуть fmt.Errorf
		return "", fmt.Errorf("ошибка загрузки файла в MinIO: %w", err)
	}

	if info == 0 {
		return "", fmt.Errorf("файл не был загружен, размер 0")
	}

	return fmt.Sprintf("/%s/%s", bucketName, fileName), nil
}

func GetMpegFile(s3 *minio.Client, backet, fileName string) (*minio.Object, error) {
	if fileName == "" {
		return nil, ErrFilenameIsRequired
	}

	// Проверяем существование бакета
	exists, err := s3.BucketExists(backet)
	if err != nil {
		return nil, ErrFailedToCheckBucketExistence
	}
	if !exists {
		return nil, ErrBucketNotFound
	}

	// Получаем объект из MinIO
	object, err := s3.GetObject(backet, fileName, minio.GetObjectOptions{})
	if err != nil {
		return nil, ErrFileNotFound
	}

	// Получаем информацию об объекте
	objectInfo, err := object.Stat()
	if err != nil {
		return nil, ErrFailedToGetFileInfo
	}

	// Проверяем, что файл имеет audio/mpeg тип
	if objectInfo.ContentType != "audio/mpeg" {
		return nil, ErrFileIsNotAnAudioMpegFile
	}

	return object, nil
}
