# Автотесты — Service Monitoring

## Как запустить

Тесты запускаются из директории `service-monitoring-main`:

```bash
cd service-monitoring-main
python3 -m pytest tests/ -v
```

## Docker
Первый раз

```bash
docker compose --profile test build tests
```

Запуск

```bash
docker compose --profile test run --rm -T tests
```

---

## Технические детали

- **База данных:** SQLite in-memory (через `StaticPool`) — PostgreSQL не нужен, Docker не нужен. Или если Docker, то PostgreSQL.
- **Изоляция:** каждый тест запускается с чистыми таблицами — данные удаляются после каждого теста.
- **Зависимости для тестов:** `pytest`, `pytest-mock`.

---

## Модули тестов

### `test_health_api.py` — Healthcheck эндпоинт

| Тест | Что проверяет |
|---|---|
| `test_health_returns_ok` | `GET /health` возвращает `{"status": "ok"}` и статус 200 |
| `test_health_content_type_is_json` | Ответ имеет заголовок `Content-Type: application/json` |

---

### `test_services_api.py` — API сервисов

| Тест | Что проверяет |
|---|---|
| `test_create_service_returns_201` | Создание сервиса возвращает HTTP 201 |
| `test_create_service_response_fields` | Ответ содержит все поля: `id`, `name`, `description`, `slaTargetPercent`, `isActive`, `createdAt`, `updatedAt` |
| `test_create_service_with_responsibles` | Ответственные сотрудники сохраняются и возвращаются в ответе |
| `test_create_service_without_responsibles` | Сервис создаётся без ответственных — поле `responsibles` пустое |
| `test_create_service_default_sla` | Если `slaTargetPercent` не указан, по умолчанию подставляется `99.9` |
| `test_create_service_multiple_responsibles` | Поддерживается несколько ответственных сотрудников |
| `test_create_service_invalid_email` | Некорректный email ответственного вызывает ошибку 422 |
| `test_create_service_missing_name` | Отсутствие поля `name` вызывает ошибку 422 |
| `test_list_services_empty` | `GET /api/v1/services` возвращает пустой список, когда нет сервисов |
| `test_list_services_after_create` | После создания сервиса список содержит одну запись |
| `test_list_services_multiple` | Список корректно содержит несколько сервисов |
| `test_get_service_by_id` | `GET /api/v1/services/{id}` возвращает сервис по его UUID |
| `test_get_service_not_found` | Несуществующий UUID возвращает 404 |
| `test_get_service_invalid_uuid` | Не-UUID строка в пути возвращает 422 |
| `test_service_id_is_uuid` | `id` созданного сервиса является валидным UUID |

---

### `test_endpoints_api.py` — API эндпоинтов сервиса

| Тест | Что проверяет |
|---|---|
| `test_create_endpoint_returns_201` | Добавление эндпоинта к сервису возвращает HTTP 201 |
| `test_create_endpoint_response_fields` | Ответ содержит `id`, `serviceId`, `name`, `url`, `method`, `timeoutMs`, `checkIntervalSec`, `isActive`, `createdAt`, `updatedAt` |
| `test_create_endpoint_default_values` | Значения по умолчанию: `method=GET`, `timeoutMs=2000`, `checkIntervalSec=10`, `isActive=true` |
| `test_create_endpoint_non_get_method_rejected` | В MVP поддерживается только `GET` — другие методы (POST и т. д.) отклоняются с 422 |
| `test_create_endpoint_service_not_found` | Добавление эндпоинта к несуществующему сервису возвращает 404 |
| `test_create_endpoint_missing_url` | Отсутствие `url` возвращает 422 |
| `test_list_endpoints_empty` | Список эндпоинтов пуст сразу после создания сервиса |
| `test_list_endpoints_after_create` | После создания эндпоинта он появляется в списке |
| `test_list_endpoints_multiple` | Список корректно отображает несколько эндпоинтов |
| `test_list_endpoints_service_not_found` | Список эндпоинтов несуществующего сервиса возвращает 404 |
| `test_get_endpoint_by_id` | `GET /api/v1/endpoints/{id}` возвращает эндпоинт по UUID |
| `test_get_endpoint_not_found` | Несуществующий UUID возвращает 404 |
| `test_patch_endpoint_url` | `PATCH` обновляет поле `url` |
| `test_patch_endpoint_timeout` | `PATCH` обновляет поле `timeoutMs` |
| `test_patch_endpoint_deactivate` | `PATCH` деактивирует эндпоинт (`isActive: false`) |
| `test_patch_endpoint_not_found` | `PATCH` несуществующего эндпоинта возвращает 404 |
| `test_patch_endpoint_partial_update_preserves_other_fields` | Частичное обновление не затирает остальные поля |

---

### `test_checks_api.py` — История проверок

| Тест | Что проверяет |
|---|---|
| `test_service_checks_empty` | История проверок пуста, если проверок ещё не было; структура ответа содержит `items`, `total`, `limit`, `offset` |
| `test_service_checks_returns_inserted_results` | Сохранённые результаты проверок (UP/DOWN) возвращаются в истории сервиса |
| `test_service_checks_filter_by_status_up` | Фильтрация по `status=UP` возвращает только успешные проверки |
| `test_service_checks_filter_by_status_down` | Фильтрация по `status=DOWN` возвращает только упавшие проверки |
| `test_service_checks_pagination` | Параметры `limit` и `offset` ограничивают количество возвращаемых записей |
| `test_service_checks_pagination_offset` | Смещение (`offset`) корректно работает — возвращает оставшиеся записи |
| `test_service_checks_date_filter` | Фильтрация по `dateFrom` исключает результаты старше указанной даты |
| `test_service_checks_result_fields` | Каждая запись истории содержит `id`, `serviceId`, `endpointId`, `checkedAt`, `status`, `createdAt` |
| `test_endpoint_checks_empty` | История проверок конкретного эндпоинта пуста изначально |
| `test_endpoint_checks_returns_results` | История проверок эндпоинта содержит сохранённые результаты |
| `test_endpoint_checks_filter_status` | Фильтрация по статусу работает для истории эндпоинта |
| `test_endpoint_checks_invalid_status` | Недопустимое значение статуса (не UP/DOWN) возвращает 422 |
| `test_service_checks_invalid_limit` | `limit=0` возвращает 422 (минимальное значение — 1) |
| `test_service_checks_limit_above_max` | `limit=9999` возвращает 422 (максимальное значение — 1000) |

---

### `test_stats_api.py` — Статистика и SLA

| Тест | Что проверяет |
|---|---|
| `test_services_summary_empty` | Сводка по всем сервисам пуста, когда нет активных сервисов |
| `test_services_summary_contains_active_service` | Созданный сервис появляется в общей сводке |
| `test_services_summary_fields` | Каждый элемент сводки содержит `serviceId`, `serviceName`, `slaTargetPercent`, `uptimePercent`, `slaBreached`, `totalChecks`, `upChecks`, `downChecks` |
| `test_services_summary_no_checks_zero_uptime` | Без проверок: `totalChecks=0`, `uptimePercent=0.0`, `slaBreached=false`, `currentStatus=null` |
| `test_services_summary_with_checks` | Счётчики `totalChecks`, `upChecks`, `downChecks` корректно рассчитываются по накопленным результатам |
| `test_service_summary_by_id` | `GET /api/v1/services/{id}/summary` возвращает сводку конкретного сервиса |
| `test_service_summary_not_found` | Сводка несуществующего сервиса возвращает 404 |
| `test_service_summary_current_status_up` | `currentStatus` отражает статус последней проверки (последняя UP → статус UP) |
| `test_service_summary_sla_breached` | `slaBreached=true`, когда uptime ниже целевого SLA (9 DOWN из 10 проверок) |
| `test_service_summary_sla_not_breached_perfect_uptime` | `slaBreached=false` при 100% uptime, `uptimePercent=100.0` |
| `test_service_stats_default_month_period` | `GET /api/v1/services/{id}/stats` возвращает статистику за период `month` |
| `test_service_stats_fields` | Ответ содержит `totalChecks`, `upChecks`, `downChecks`, `uptimePercent`, `slaTargetPercent`, `slaBreached` |
| `test_service_stats_uptime_calculation` | Uptime рассчитывается корректно: 3 UP + 1 DOWN = 75.00% |
| `test_service_stats_not_found` | Статистика несуществующего сервиса возвращает 404 |
| `test_service_stats_no_checks_zero` | Без проверок: `totalChecks=0`, `uptimePercent=0.0`, `slaBreached=false` |

---

### `test_health_check_service.py` — Логика HTTP-проверки эндпоинтов

Юнит-тесты для `app/services/health_check_service.py`. HTTP-запросы мокируются — реальных сетевых вызовов нет.

| Тест | Что проверяет |
|---|---|
| `test_check_endpoint_200_returns_up` | HTTP 200 → статус `UP`, нет ошибки |
| `test_check_endpoint_200_has_latency` | При успешной проверке `latency_ms` заполнен и ≥ 0 |
| `test_check_endpoint_500_returns_down` | HTTP 500 → статус `DOWN`, `error_type=HTTP_5XX`, сообщение содержит «500» |
| `test_check_endpoint_503_returns_down` | HTTP 503 → статус `DOWN`, `error_type=HTTP_5XX` |
| `test_check_endpoint_404_returns_down` | HTTP 404 (неожиданный статус) → `DOWN`, `error_type=UNKNOWN_ERROR` |
| `test_check_endpoint_301_returns_down` | HTTP 301 (редирект) → `DOWN` (только 200 считается UP) |
| `test_check_endpoint_timeout_returns_down` | Таймаут соединения → `DOWN`, `error_type=TIMEOUT`, `http_status_code=None` |
| `test_check_endpoint_connect_error_returns_down` | Ошибка соединения → `DOWN`, `error_type=CONNECTION_ERROR` |
| `test_check_endpoint_generic_http_error_returns_down` | Прочие `HTTPError` → `DOWN`, `error_type=UNKNOWN_ERROR` |
| `test_check_endpoint_unexpected_exception_returns_down` | Любое непредвиденное исключение → `DOWN`, `error_type=UNKNOWN_ERROR` |
| `test_check_endpoint_sets_service_and_endpoint_id` | Результат содержит правильные `service_id` и `endpoint_id` |
| `test_check_endpoint_checked_at_is_recent` | `checked_at` — текущее UTC-время (не из прошлого и не из будущего) |
| `test_check_endpoint_error_message_set_on_timeout` | При таймауте `error_message` не пустой |

---

### `test_datetime_utils.py` — Утилита границ месяца

Юнит-тесты для `app/utils/datetime_utils.py::get_current_month_bounds`.

| Тест | Что проверяет |
|---|---|
| `test_month_bounds_returns_tuple_of_two_datetimes` | Функция возвращает кортеж из двух `datetime` |
| `test_month_start_is_first_day` | Начало месяца — всегда 1-е число |
| `test_month_start_is_midnight` | Начало месяца — 00:00:00.000000 |
| `test_month_end_is_first_day_of_next_month` | Конец месяца — 1-е число следующего месяца |
| `test_month_bounds_are_timezone_aware` | Оба datetime содержат timezone info |
| `test_month_bounds_with_explicit_january` | Январь 2025: начало `2025-01-01`, конец `2025-02-01` |
| `test_month_bounds_with_explicit_december` | Декабрь 2024: начало `2024-12-01`, конец `2025-01-01` (корректный переход года) |
| `test_month_bounds_with_naive_datetime` | Naive datetime (без timezone) принимается и обрабатывается корректно |
| `test_month_bounds_end_greater_than_start` | Конец всегда позже начала |
| `test_month_bounds_span_exactly_one_month` | Разница между началом и концом — от 28 до 31 дня |
| `test_month_bounds_for_february_non_leap` | Февраль 2025 (не високосный) — 28 дней |
| `test_month_bounds_for_february_leap` | Февраль 2024 (високосный) — 29 дней |

---

### `test_result_sla_service.py` — Расчёт SLA и сохранение результатов

Юнит-тесты для `app/services/result_sla_service.py`. БД мокируется.

#### `TestIsDown` — Вспомогательная функция `_is_down`

| Тест | Что проверяет |
|---|---|
| `test_down_status_enum_is_down` | `CheckStatus.DOWN` (enum) → `True` |
| `test_up_status_enum_is_not_down` | `CheckStatus.UP` (enum) → `False` |
| `test_down_string_is_down` | Строка `"DOWN"` → `True` |
| `test_up_string_is_not_down` | Строка `"UP"` → `False` |

#### `TestStatusValue` — Вспомогательная функция `_status_value`

| Тест | Что проверяет |
|---|---|
| `test_none_returns_none` | `None` → `None` |
| `test_up_returns_string` | `CheckStatus.UP` → строка `"UP"` |
| `test_down_returns_string` | `CheckStatus.DOWN` → строка `"DOWN"` |

#### `TestCalculateMonthlyMetrics` — Расчёт ежемесячных метрик

| Тест | Что проверяет |
|---|---|
| `test_no_results_returns_zeros` | Без проверок: все счётчики 0, `uptime=0.00`, `sla_breached=False` |
| `test_all_up_100_percent` | 10 из 10 UP → `uptime=100.00`, SLA не нарушен |
| `test_all_down_0_percent_and_sla_breached` | 5 из 5 DOWN → `uptime=0.00`, SLA нарушен |
| `test_mixed_uptime_calculation` | 3 UP + 1 DOWN = 4 проверки → `uptime=75.00`, SLA нарушен |
| `test_sla_not_breached_at_exact_target` | 999 UP + 1 DOWN из 1000 → `uptime=99.90`, SLA не нарушен (граничный случай) |
| `test_uptime_rounded_to_two_decimals` | 2 UP + 1 DOWN → `uptime=66.67` (округление до 2 знаков) |

#### `TestSaveCheckResult` — Сохранение результата и уведомления

| Тест | Что проверяет |
|---|---|
| `test_save_up_result_does_not_trigger_notification` | Результат UP — уведомление НЕ отправляется |
| `test_save_down_result_triggers_notification` | Результат DOWN — уведомление отправляется один раз |
