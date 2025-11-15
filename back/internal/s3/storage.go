package s3

import "github.com/minio/minio-go"

// FileManager интерфейс для управления файлами в объектном хранилище.
type FileManager interface {
	// UploadFile загружает файл в объектное хранилище
	// Возвращает путь к файлу или ошибку в случае неудачи
	UploadFile(bucketName, uuid, fileExtension string, fileData []byte, contentType string) (string, error)

	// GetFile получает файл из объектного хранилища
	// Возвращает объект файла или ошибку в случае неудачи
	GetFile(bucket, fileName string) (*minio.Object, error)

	// ValidateFileSize проверяет размер файла перед загрузкой
	// Возвращает ошибку если размер превышает допустимый или файл пустой
	ValidateFileSize(fileData []byte) error

	// GetMaxFileSize возвращает максимальный разрешенный размер файла
	GetMaxFileSize() int64
}

// AudioFileManager интерфейс для работы с аудиофайлами в объектном хранилище.
type AudioFileManager interface {
	// UploadMP3 загружает MP3 файл в объектное хранилище
	// Возвращает путь к файлу или ошибку в случае неудачи
	Upload(bucketName, uuid string, mp3Data []byte) (string, error)

	// GetMP3File получает MP3 файл из объектного хранилища
	// Возвращает объект файла или ошибку, если файл не найден или не является MP3
	Get(bucket, fileName string) (*minio.Object, error)
}
