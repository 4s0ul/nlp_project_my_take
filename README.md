# 🚀 Руководство по быстрому запуску

Этот документ описывает, как собрать, запустить и заполнить данными бэкенд **dictionary** и его базу данных Postgres.

---

## Требования

* Docker и Docker Compose
* Python 3.8+

---

## 1. Сборка образа бэкенда

Из корня проекта выполните:

```bash
docker build -t dictionary/backend:1.0 ./backend
```

---

## 2. Запуск сервисов

Поднимите базу данных и бэкенд:

```bash
docker compose up -d
```

* **Postgres + pgvector** будет доступен на `localhost:54321` (проброшен в контейнерный `5432`).
* **Бэкенд (FastAPI + Uvicorn)** запустится на `localhost:8001` (проброшен в контейнерный `8000`).

Проверьте состояние:

```bash
# Список работающих контейнеров
docker ps

# Логи бэкенда
docker logs -f backend
```

После запуска интерфейс документации OpenAPI будет доступен по адресу:

```
http://localhost:8001/docs
```

---

## 3. Заполнение базы данных

Используйте скрипт `fill_db.py` для загрузки терминов и описаний из JSON-файлов. Каждый файл соответствует одной «теме» (topic) в БД.

```bash
# Физические термины
python3 backend/fill_db.py \
  --json backend/filler_data/fiz_terms.json \
  --topic "Physical Terms" \
  --info "Термины по физике"

# Химические термины
python3 backend/fill_db.py \
  --json backend/filler_data/him_terms.json \
  --topic "Chemistry Terms" \
  --info "Термины по химии"

# Данные Менделеева (также химия)
python3 backend/fill_db.py \
  --json backend/filler_data/mendeleev_terms.json \
  --topic "Chemistry Terms" \
  --info "Термины по химии"

# Совмещённые физико-химические термины
python3 backend/fill_db.py \
  --json backend/filler_data/fizhim_terms.json \
  --topic "FizHim Terms" \
  --info "Термины физ-хим"
