Клонуйте репозиторій:
git clone https://github.com/your-repo.git
cd your-repo
Встановіть необхідні залежності:
pip install -r requirements.txt
Створіть базу даних і відредагуйте файл .env для налаштувань бази даних та секретного ключа:
CREATE DATABASE dbname
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
SECRET_KEY=your_secret_key


Запуск проекту:
uvicorn app.main:app --reload
Запуск тестів:
pytest

Ендпоінти:

Реєстрація користувачів
POST /register
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "password123"
}

Вхід користувачів
POST /token
{
  "username": "user1",
  "password": "password123"
}
Управління постами
POST /posts/
{
  "title": "My Post",
  "content": "This is my post content"
}
GET /posts/

Управління коментарями

POST /comments/?post_id={post_id}
{
  "content": "This is a comment"
}
GET /comments/

Аналітика коментарів
GET /api/comments-daily-breakdown?date_from=2020-02-02&date_to=2022-02-15