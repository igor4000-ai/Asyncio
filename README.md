# Star Wars API Async Data Loader

Асинхронный пайплайн для загрузки персонажей Star Wars из SWAPI в PostgreSQL.

## Требования

- Python 3.10+
- Docker и Docker Compose

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Разверните PostgreSQL в Docker:
```bash
docker compose up -d
```

## Использование

1. Создайте таблицы в базе данных:
```bash
python migrate.py
```

2. Загрузите данные из SWAPI:
```bash
python load_data.py
```

3. Проверьте количество загруженных персонажей:
```bash
docker exec -it swapi_postgres psql -U swapi_user -d swapi_db -c "SELECT COUNT(*) FROM people;"
```

## Структура проекта

- `models.py` — SQLAlchemy модель для таблицы `people`
- `migrate.py` — скрипт для создания таблиц
- `load_data.py` — асинхронный скрипт загрузки данных из SWAPI
- `docker-compose.yml` — конфигурация PostgreSQL
- `requirements.txt` — зависимости Python

## API

Данные загружаются из [SWAPI](https://swapi-node.vercel.app):
- Список персонажей: `GET /api/people/?page=1&limit=10`
- Детали персонажа: `GET /api/people/{id}`

Все HTTP-запросы выполняются асинхронно через `aiohttp`.
