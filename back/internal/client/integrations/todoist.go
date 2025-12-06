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

type Todoist struct {
	url    string
	client *http.Client
	logger *logrus.Logger
}

func NewTodoist(url string, logger *logrus.Logger) *Todoist {
	return &Todoist{
		url:    url,
		client: &http.Client{},
		logger: logger,
	}
}

// SaveToken проксирует запрос на сохранение токена Todoist.
func (t *Todoist) SaveToken(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/todoist/auth/save")
}

// GetStatus проксирует запрос на получение статуса авторизации Todoist.
func (t *Todoist) GetStatus(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/todoist/status")
}

// GetProjects проксирует запрос на получение проектов Todoist.
func (t *Todoist) GetProjects(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/todoist/projects")
}

// CreateTask проксирует запрос на создание задачи в Todoist.
func (t *Todoist) CreateTask(c *fiber.Ctx) error {
	return t.proxyRequest(c, "/todoist/create/task")
}

// proxyRequest общий метод для проксирования запросов.
func (t *Todoist) proxyRequest(c *fiber.Ctx, endpoint string) error {
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
	t.logger.Infof("Proxying request to: %s", url)
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
