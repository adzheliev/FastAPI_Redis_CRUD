# FastAPI Phone → Address Service

CRUD-API для хранения связки "номер телефона → адрес клиента"  
с валидацией номера и сохранением данных в Redis.

---

## Функционал

| Метод  | Endpoint         | Описание                          |
|-------:|------------------|----------------------------------|
| POST   | `/phones`        | Создать запись phone → address   |
| GET    | `/phones/{phone}`| Получить запись по номеру        |
| PUT    | `/phones/{phone}`| Обновить адрес                   |
| DELETE | `/phones/{phone}`| Удалить запись                    |

Телефон автоматически нормализуется в формат `+79991234567`.  
Искать можно в любом пользовательском виде:  
`+7...`, `8 (999)...`, `8999...` — результат будет найден.

---

## Запуск через Docker
```bash
docker compose up --build -d
```

## После запуска API доступен по адресу:
`http://localhost:8000`

## Swagger UI:
`http://localhost:8000/docs`

## Healthcheck:
`http://localhost:8000/health`

## Остановка сервиса:
```bash
docker compose down
```