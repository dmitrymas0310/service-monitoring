# MVP системы мониторинга сервисов

Локальные URL:

- Monitoring Service: http://localhost:8000
- Test Service: http://localhost:8081
- Mailpit UI: http://localhost:8025

Запуск всех сервисов:

```bash
docker compose up --build
```

## Демонстрационный сценарий

1. Запустите весь MVP:

```bash
docker compose up --build
```

2. Зарегистрируйте `test-service` и ответственного сотрудника:

```bash
curl -s -X POST http://localhost:8000/api/v1/services \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-service",
    "description": "Demo service for monitoring UP, DOWN and TIMEOUT scenarios",
    "slaTargetPercent": 99.9,
    "responsibles": [
      {
        "fullName": "Demo User",
        "email": "demo@example.com"
      }
    ]
  }'
```

Сохраните возвращённый `id` в переменную `SERVICE_ID`

3. Добавьте демонстрационные endpoint’ы. Внутри Docker Compose используйте `http://test-service:8081/...`, потому что сервисы находятся в одной Docker-сети.

```bash
curl -s -X POST "http://localhost:8000/api/v1/services/${SERVICE_ID}/endpoints" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test health UP",
    "url": "http://test-service:8081/health/up",
    "method": "GET",
    "timeoutMs": 2000,
    "checkIntervalSec": 10,
    "isActive": true
  }'
```

```bash
curl -s -X POST "http://localhost:8000/api/v1/services/${SERVICE_ID}/endpoints" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test health DOWN",
    "url": "http://test-service:8081/health/down",
    "method": "GET",
    "timeoutMs": 2000,
    "checkIntervalSec": 10,
    "isActive": true
  }'
```

```bash
curl -s -X POST "http://localhost:8000/api/v1/services/${SERVICE_ID}/endpoints" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test health TIMEOUT",
    "url": "http://test-service:8081/health/timeout",
    "method": "GET",
    "timeoutMs": 2000,
    "checkIntervalSec": 10,
    "isActive": true
  }'
```

4. Подождите несколько циклов scheduler. По умолчанию проверки выполняются каждые 10 секунд.

5. Проверьте историю проверок сервиса:

"http://localhost:8000/api/v1/services/${SERVICE_ID}/checks?limit=100&offset=0"


Опциональный фильтр по статусу:

"http://localhost:8000/api/v1/services/${SERVICE_ID}/checks?status=DOWN&limit=100&offset=0"


6. Проверьте месячный SLA и uptime:

"http://localhost:8000/api/v1/services/${SERVICE_ID}/stats?period=month"


7. Проверьте сводку по сервисам:

http://localhost:8000/api/v1/services/summary


Сводка по одному сервису:

"http://localhost:8000/api/v1/services/${SERVICE_ID}/summary"


8. Откройте Mailpit UI и проверьте email-уведомления для проверок `DOWN` и `TIMEOUT`:

http://localhost:8025

