package client

type MessageStreamClient interface {
    // StreamRequestToModel основной метод для потоковых запросов
    StreamRequestToModel(payload PayloadStream) (<-chan *StreamMessage, string, error)
    
    // Ping проверка здоровья сервиса
    Ping() error
}