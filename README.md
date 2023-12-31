# Сервис авторизации

### Описание
Микросервис аутентификации и авторизации пользователей с интерактивной системой ролей, выполненный в виде асинхронного API (FastAPI) с использованием JWT-токенов. Все эндпоинты API покрыты асинхронными тестами (pytest, pytest-asyncio).
Автор: Аюпов Ильдар, 2023 г., ildarbon@gmail.com
Основные технологии и библиотеки:
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- pydantic
- async-fastapi-jwt-auth
- Docker
- Nginx
- Pytest
- Pytest-asyncio
- aiohttp

### Инструкция по запуску API
- клонировать настоящий репозиторий
- в папке ```fastapi``` переименовать файл ```.env.example``` в ```.env``` (все настройки рабочие; ничего менять не нужно)
- в папке ```fastapi``` выполнить команду ```docker compose up```. Отобразится процесс сборки контейнеров, после чего API заработает.
- при сборке контейнеров автоматически создается суперпользователь командой ```python createsuperuser.py admin admin``` (логин ```admin``` и пароль ```admin```). Эти учетные данные необходимы для начала работы с ролями в API (группа ендпоинтов ```api/v1/manage/...```) и для тестов. При необходимости можно создать и другие учетные записи суперпользователей, используя шаблон команды ```python createsuperuser.py LOGIN PASSWORD```
- после сборки контейнеров эндпоинты API доступны по адресам: ```127.0.0.1/api/v1/users/...``` и ```127.0.0.1/api/v1/manage/...```
- подробное описание API доступно по адресу ```127.0.0.1/api/openapi```

### Инструкция по запуску тестов к API
- клонировать настоящий репозиторий
- в папке ```tests/functional``` переименовать файл ```.env.example``` в ```.env``` (все настройки рабочие; ничего менять не нужно)
- в папке ```tests/functional``` выполнить команду ```docker compose up```. Отобразится процесс сборки контейнеров и ход выполнения тестов.

