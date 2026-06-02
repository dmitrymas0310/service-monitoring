# Отчет о ручном тестировании API

Дата прогона: 2026-05-31.

## Стенд

* Docker Desktop: доступен, context `desktop-linux`.
* Запуск проекта: `docker compose up -d --build`.
* Monitoring Service: `http://localhost:8000`.
* Test Service: `http://localhost:8081`.
* Mailpit UI: `http://localhost:8025`.
* PostgreSQL: контейнер `monitoring-db`, БД `monitoring_db`.
* Интервал scheduler: `CHECK_INTERVAL_SECONDS=10` из `.env`.

Состояние контейнеров во время проверки:

* `monitoring-db`: `Up`, `healthy`.
* `test-service`: `Up`.
* `mailpit`: `Up`, `healthy`.
* `monitoring-service`: `Up`.

После завершения проверки `monitoring-service` был остановлен командой:

```bash
docker compose stop monitoring-service
```

Это было сделано, чтобы scheduler не создавал новые проверки и письма после завершения тестового прогона.

## Тестовые данные

* `serviceId`: `77b5d84d-df40-49d4-942b-8120e80a49bd`
* `UP endpointId`: `57f983d8-cc93-4e1f-9197-dc41a8a7cfa7`
* `DOWN endpointId`: `219cc266-fd47-43aa-bb48-9bbd54b1b76c`
* `TIMEOUT endpointId`: `3cc7dd88-9517-49f0-9780-11589643e9ae`

Endpoint URL регистрировались через Docker-сеть:

* `http://test-service:8081/health/up`
* `http://test-service:8081/health/down`
* `http://test-service:8081/health/timeout`

## Сценарии и результаты

| ID    | Сценарий                                      | Запрос                                                                   | Ожидаемый результат                                                             | Фактический результат                                                                                          | Статус |
| ----- | --------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------ |
| MT-01 | Healthcheck Monitoring Service                | `GET /health`                                                            | `200`, `{"status":"ok"}`                                                        | `200`, `{"status":"ok"}`                                                                                       | PASS   |
| MT-02 | Healthcheck Test Service                      | `GET http://localhost:8081/health`                                       | `200`, `{"status":"ok"}`                                                        | `200`, `{"status":"ok"}`                                                                                       | PASS   |
| MT-03 | Доступность Mailpit UI                        | `GET http://localhost:8025`                                              | `200`                                                                           | `200`                                                                                                          | PASS   |
| MT-04 | Создание сервиса с ответственным              | `POST /api/v1/services`                                                  | `201`, сервис создан                                                            | `201`, сервис создан, `slaTargetPercent=99.90`, добавлен 1 ответственный                                       | PASS   |
| MT-05 | Получение списка сервисов                     | `GET /api/v1/services`                                                   | `200`, созданный сервис есть в списке                                           | `200`, сервис найден в списке                                                                                  | PASS   |
| MT-06 | Получение сервиса по ID                       | `GET /api/v1/services/{serviceId}`                                       | `200`, возвращаются данные сервиса                                              | `200`, данные совпадают с созданным сервисом                                                                   | PASS   |
| MT-07 | Получение несуществующего сервиса             | `GET /api/v1/services/00000000-0000-0000-0000-000000000000`              | `404`                                                                           | `404`                                                                                                          | PASS   |
| MT-08 | Обновление сервиса                            | `PATCH /api/v1/services/{serviceId}`                                     | Согласно `docs/swagger.yaml`: `200`, сервис обновлен                            | `405 Method Not Allowed`                                                                                       | FAIL   |
| MT-09 | Создание сервиса без ответственных            | `POST /api/v1/services` с `responsibles: []`                             | Согласно `docs/swagger.yaml`, ожидается ошибка валидации, так как `minItems: 1` | `201`, сервис создан без ответственных                                                                         | FAIL   |
| MT-10 | Создание endpoint'ов UP, DOWN и TIMEOUT       | `POST /api/v1/services/{serviceId}/endpoints`                            | `201` для каждого endpoint                                                      | Все 3 endpoint успешно созданы                                                                                 | PASS   |
| MT-11 | Получение endpoint'ов сервиса                 | `GET /api/v1/services/{serviceId}/endpoints`                             | `200`, возвращаются 3 endpoint'а                                                | `200`, вернулись UP, DOWN и TIMEOUT endpoint'ы                                                                 | PASS   |
| MT-12 | Получение endpoint по ID                      | `GET /api/v1/endpoints/{endpointId}`                                     | `200`, возвращаются данные endpoint                                             | `200`, данные UP endpoint совпадают                                                                            | PASS   |
| MT-13 | Частичное обновление endpoint                 | `PATCH /api/v1/endpoints/{endpointId}`                                   | `200`, обновлены `timeoutMs` и `checkIntervalSec`                               | `200`, значения обновлены: `timeoutMs=2500`, `checkIntervalSec=12`                                             | PASS   |
| MT-14 | Создание endpoint для несуществующего сервиса | `POST /api/v1/services/{fakeId}/endpoints`                               | `404`                                                                           | `404`                                                                                                          | PASS   |
| MT-15 | Создание endpoint с неподдерживаемым методом  | `POST /api/v1/services/{serviceId}/endpoints` с `method=POST`            | Ошибка валидации                                                                | `422 Unprocessable Content`                                                                                    | PASS   |
| MT-16 | Автоматические проверки scheduler'ом          | Ожидание нескольких scheduler-циклов                                     | В истории появляются результаты UP, HTTP_5XX и TIMEOUT                          | Контрольный срез: `UP=7`, `DOWN=14`, из них `HTTP_5XX=7` и `TIMEOUT=7`                                         | PASS   |
| MT-17 | История проверок сервиса                      | `GET /api/v1/services/{serviceId}/checks?limit=200&offset=0`             | `200`, возвращается список результатов                                          | `200`, `total=21`                                                                                              | PASS   |
| MT-18 | История проверок с фильтром DOWN              | `GET /api/v1/services/{serviceId}/checks?status=DOWN&limit=200&offset=0` | `200`, возвращаются только DOWN-проверки                                        | `200`, `total=14`                                                                                              | PASS   |
| MT-19 | История проверок endpoint'а UP                | `GET /api/v1/endpoints/{upEndpointId}/checks`                            | `200`, история конкретного endpoint                                             | `200`, `total=7`                                                                                               | PASS   |
| MT-20 | История проверок endpoint'а DOWN              | `GET /api/v1/endpoints/{downEndpointId}/checks`                          | `200`, история конкретного endpoint                                             | `200`, `total=7`, ошибки `HTTP_5XX`                                                                            | PASS   |
| MT-21 | История проверок endpoint'а TIMEOUT           | `GET /api/v1/endpoints/{timeoutEndpointId}/checks`                       | `200`, история конкретного endpoint                                             | `200`, `total=7`, ошибки `TIMEOUT`                                                                             | PASS   |
| MT-22 | Расчет SLA за месяц                           | `GET /api/v1/services/{serviceId}/stats?period=month`                    | `200`, рассчитаны счетчики и SLA                                                | `200`, `totalChecks=21`, `upChecks=7`, `downChecks=14`, `uptimePercent=33.33`, `slaBreached=true`              | PASS   |
| MT-23 | Сводка по сервису                             | `GET /api/v1/services/{serviceId}/summary`                               | `200`, возвращаются текущий статус и SLA                                        | `200`, `currentStatus=UP`, `totalChecks=21`, `upChecks=7`, `downChecks=14`, `lastError=null`                   | PASS   |
| MT-24 | Общая сводка по сервисам                      | `GET /api/v1/services/summary`                                           | `200`, возвращается список активных сервисов                                    | `200`, вернулись созданные активные сервисы, включая `compose-manual-test-service` и `compose-no-responsibles` | PASS   |
| MT-25 | Некорректный период статистики                | `GET /api/v1/services/{serviceId}/stats?period=week`                     | Ошибка валидации периода                                                        | `422 Unprocessable Content`                                                                                    | PASS   |

## Проверка уведомлений

Mailpit был доступен по адресу `http://localhost:8025`. После DOWN и TIMEOUT проверок письма появились в Mailpit.

Финальный срез Mailpit после остановки `monitoring-service`:

```json
{
  "total": 24,
  "unread": 24
}
```

Примеры тем писем:

* `[Monitoring] DOWN: compose-manual-test-service / DOWN endpoint`
* `[Monitoring] DOWN: compose-manual-test-service / TIMEOUT endpoint`

Также была проверена таблица `notification_log` в PostgreSQL:

```sql
select status, count(*)
from notification_log
group by status
order by status;
```

Результат:

```text
 status | count
--------+-------
 SENT   |    24
```

Итог проверки уведомлений: письма успешно доставляются в Mailpit, а записи в `notification_log` сохраняются со статусом `SENT`.

## Найденные расхождения

1. `PATCH /api/v1/services/{serviceId}` описан в `docs/swagger.yaml`, но фактически не реализован в `app/api/services_api.py`. API возвращает `405 Method Not Allowed`.

2. `responsibles` в Swagger описан как обязательный массив с `minItems: 1`, но фактически `POST /api/v1/services` принимает `responsibles: []` и создает сервис без ответственных.

3. Для `POST /api/v1/services/{serviceId}/endpoints` Swagger декларирует `400` на некорректные данные, но при передаче неподдерживаемого `method=POST` возвращается `422 Unprocessable Content`.

4. Поле `checkIntervalSec` сохраняется у endpoint, но проверки выполняются по глобальному scheduler-интервалу `CHECK_INTERVAL_SECONDS`. Индивидуальный интервал endpoint'а не используется как отдельное расписание проверок.

5. В сводке по сервису `currentStatus=UP`, хотя в истории сервиса есть DOWN/TIMEOUT проверки. Возможно, статус рассчитывается по последней проверке или по отдельной логике, но это стоит дополнительно уточнить в реализации.

## Итог

На compose-стенде с PostgreSQL и Mailpit основные сценарии работают корректно: создание сервиса, создание endpoint'ов, автоматические проверки, получение истории, расчет SLA, получение сводок и отправка email-уведомлений.

Основные замечания связаны с расхождением фактической реализации и `docs/swagger.yaml`, а также с отсутствием валидации обязательного ответственного при создании сервиса.
