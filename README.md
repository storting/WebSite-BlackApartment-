# WebSite-BlackApartment-
Основная цель заказчика - это заработок. Хотим решить проблемемы автоматизации процесса подбора недвижимости для клиента и презентабельность. Требования: Регистрация, выбор города, лента поиска, фильтрация, онлайн оплата, мини-карта. Рассматривается краткосрочная аренда. Проект должен быть выполнен в виде веб-сайта, с адаптивным интерфейсом.

# 1. Что нужно установить перед запуском

    Docker Engine + Docker Compose (входят в Docker Desktop или устанавливаются отдельно)

Проверка:
bash

docker --version
docker compose version

# 2. Клонирование репозитория
bash

git clone https://github.com/startting/Website-Blackapartment-.git BlackApart
cd BlackApart

# 3. Настройка окружения

Создайте файл .env (на основе примера ниже):
bash

nano .env

text

SECRET_KEY=секретный_ключ_сгенерируйте
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

    Секретный ключ можно получить командой:
    python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Запуск всех сервисов
bash

docker compose up -d --build

Что будет запущено (в одном контейнере):

    Gunicorn + Django (внутренний порт 8000)

    Nginx (как reverse proxy, порт 80 на хосте)

    SQLite (файл базы данных хранится на хосте, данные не теряются)

    Примечание: В данном проекте используется системный Nginx на хосте, но для портативности можно добавить контейнер с Nginx. Финальная конфигурация описана в docker-compose.yml.

# 5. Проверка, что всё поднялось
bash

docker compose ps

Вывод должен показывать статус Up для сервиса web.

# 6. Адреса после запуска

    Сайт: http://localhost (или IP сервера)

    Админка Django: http://localhost/admin

# 7. Первичная настройка

Примените миграции, соберите статику и создайте суперпользователя:
bash

docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser

# 8. Как остановить проект
bash

docker compose down

Полная очистка (удаление томов с данными):
bash

docker compose down -v

# 9. Полезные команды для диагностики
bash

# Логи контейнера
docker compose logs -f web

# Пересборка и перезапуск
docker compose up -d --build

# Вход в контейнер
docker compose exec web bash

# 10. Структура проекта (основные файлы)
text

BlackApart/
├── BlackApart/            # Django-проект (settings, wsgi) 
├── BlackApp/              # Приложение 
├── templates/             # Шаблоны 
├── static/                # Исходная статика 
├── media/                 # Загруженные файлы (том на хосте) 
├── requirements.txt       # Зависимости Python 
├── Dockerfile             # Сборка образа 
├── docker-compose.yml     # Оркестрация 
└── .env                   # Переменные окружения 

# 11. Для разработчиков (локальная среда)

Если нужно разрабатывать без Docker:

    Python 3.11+

    Установите зависимости: pip install -r requirements.txt

    Настройте БД (SQLite или PostgreSQL)

    Запуск: python manage.py runserver

Но рекомендуемый способ для тестирования и деплоя — только через Docker.
# 12. Если что-то не работает

    Проверьте, что Docker работает: docker ps

    Посмотрите логи: docker compose logs web

    Пересоберите контейнеры: docker compose up -d --build

    Убедитесь, что порт 80 не занят другим процессом (например, системным Nginx)
