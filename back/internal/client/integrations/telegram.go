package integrations

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/gofiber/fiber/v2"
	"github.com/sirupsen/logrus"
)

type Telegram struct {
	url    string
	client *http.Client
	logger *logrus.Logger
}

func NewTelegram(url string, logger *logrus.Logger) *Telegram {
	return &Telegram{
		url:    url,
		client: &http.Client{},
		logger: logger,
	}
}

// StartAuth проксирует запрос на начало авторизации Telegram.
func (t *Telegram) StartAuth(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/telegram/user/auth/start")
}

// VerifyAuth проксирует запрос на подтверждение авторизации Telegram.
func (t *Telegram) VerifyAuth(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/telegram/user/auth/verify")
}

// GetStatus проксирует запрос на получение статуса Telegram пользователя.
func (t *Telegram) GetStatus(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/telegram/user/status")
}

// GetContacts проксирует запрос на получение контактов Telegram.
func (t *Telegram) GetContacts(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/telegram/user/contacts")
}

// SendMessage проксирует запрос на отправку сообщения в Telegram.
func (t *Telegram) SendMessage(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/telegram/user/send/message")
}

// Disconnect проксирует запрос на отключение Telegram пользователя.
func (t *Telegram) Disconnect(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/telegram/user/disconnect")
}

// proxyRequest общий метод для проксирования запросов.
func (t *Telegram) proxyRequest(c *fiber.Ctx, endpoint string) error {
	// Получаем тело запроса
	body := c.Body()
	if len(body) == 0 {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Request body is empty",
		})
	}

	// Проверяем валидность JSON
	var jsonBody map[string]interface{}
	if err := json.Unmarshal(body, &jsonBody); err != nil {
		t.logger.Errorf("Invalid JSON body: %v", err)
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid JSON format",
		})
	}

	// Создаем запрос к оригинальному серверу
	url := t.url + endpoint
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewBuffer(body))
	if err != nil {
		t.logger.Errorf("Failed to create request: %v", err)
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to create request",
		})
	}

	// Копируем заголовки
	c.Request().Header.VisitAll(func(key, value []byte) {
		req.Header.Set(string(key), string(value))
	})

	// Устанавливаем заголовок Content-Type если его нет
	if req.Header.Get("Content-Type") == "" {
		req.Header.Set("Content-Type", "application/json")
	}

	// Выполняем запрос
	t.logger.Infof("Proxying Telegram request to: %s", url)
	resp, err := t.client.Do(req)
	if err != nil {
		t.logger.Errorf("Failed to proxy request: %v", err)
		return c.Status(fiber.StatusBadGateway).JSON(fiber.Map{
			"error": fmt.Sprintf("Failed to connect to upstream: %v", err),
		})
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			println("Ошибка при закрытии тела запроса: ", err.Error())
		}
	}()

	// Читаем ответ
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		t.logger.Errorf("Failed to read response body: %v", err)
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to read response",
		})
	}

	// Копируем заголовки ответа, исключая CORS заголовки (их устанавливает бэкенд)
	corsHeaders := map[string]bool{
		"Access-Control-Allow-Origin":      true,
		"Access-Control-Allow-Methods":    true,
		"Access-Control-Allow-Headers":    true,
		"Access-Control-Allow-Credentials": true,
		"Access-Control-Expose-Headers":   true,
		"Access-Control-Max-Age":         true,
	}
	
	for key, values := range resp.Header {
		// Пропускаем CORS заголовки - их устанавливает бэкенд
		if corsHeaders[key] {
			continue
		}
		for _, value := range values {
			c.Response().Header.Add(key, value)
		}
	}

	// Возвращаем ответ
	c.Status(resp.StatusCode)
	return c.Send(respBody)
}
