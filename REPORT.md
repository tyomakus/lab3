# Отчет о выполнении лабораторной работы

## № 3: Веб-приложение для управления статьями с использованием PostgreSQL, MongoDB и Redis

**Дата:** 2026-04-01
**Предметная область:** Газетная редакция (управление статьями, авторами, категориями, выпусками)

---

## 1. ОПИСАНИЕ ПРИЛОЖЕНИЯ

### 1.1 Общая архитектура

Приложение представляет собой многоуровневое веб-приложение на базе **FastAPI** с использованием трех типов баз данных:

```
Клиент (Браузер)
    ↓ HTTP (GET/POST)
    ↓
FastAPI (Сервер)
    ├─→ PostgreSQL (основные данные)
    ├─→ MongoDB (комментарии и статистика)
    └─→ Redis (кеш и рейтинги)
```

### 1.2 Предметная область

**Газетная редакция** - система управления и публикации статей с функциями:
- Создания и просмотра статей
- Управления авторами и категориями
- Комментирования и оценки статей
- Статистики просмотров и популярности
- Поиска статей по названию и содержимому

---

## 2. ВЕБ-ПРИЛОЖЕНИЕ

### 2.1 Технологический стек

```
Frontend:
  - HTML/CSS (Bootstrap 5.3)
  - Jinja2 템플릿
  - JavaScript (QRCode, копирование ссылок)

Backend:
  - FastAPI 0.109.1
  - SQLAlchemy 2.0 (async)
  - Motor 4.3.4 (MongoDB async)
  - Redis 5.6.0 (async)
```

### 2.2 Реализованные страницы (7 страниц)

| №  | URL | Название | Описание |
|----|----|----------|---------|
| 1  | `/` | Главная (Все статьи) | Список всех статей из PostgreSQL |
| 2  | `/articles/{id}` | Детали статьи | Полная информация о статье с комментариями и рейтингом |
| 3  | `/articles/new` | Добавление статьи | Форма для создания новой статьи с выбором автора, категории, выпуска |
| 4  | `/search` | Поиск | Поиск статей по названию/содержимому с фильтром по рейтингу |
| 5  | `/popular` | Популярные статьи | Топ статей по просмотрам из Redis |
| 6  | `/authors` | Авторы | Список авторов с добавлением новых |
| 7  | `/statistics` | Статистика | **Демонстрация всех БД и запросов** (GROUP BY, JOIN, агрегация) |

### 2.3 Функциональность

#### Основные операции:
- ✅ Создание/просмотр/редактирование статей
- ✅ Просмотр с подсчетом в Redis
- ✅ Комментирование статей в MongoDB
- ✅ Оценка (рейтинг) с средним вычислением
- ✅ Поиск с фильтрацией
- ✅ Статистика с GROUP BY, JOIN, агрегацией

---

## 3. БАЗА ДАННЫХ PostgreSQL

### 3.1 Схема БД (3NF нормализация)

```
┌─────────────┐
│   AUTHORS   │
├─────────────┤
│ id (PK)     │◄─┐
│ name        │  │  1:M
│ email (UQ)  │  │
└─────────────┘  │
                 │
            ┌────────────────┐
            │   ARTICLES     │
            ├────────────────┤
            │ id (PK)        │
            │ title          │◄─┐
            │ content        │  │
            │ author_id (FK) ├──┘
            │ category_id(FK)├──┐
            │ issue_id (FK)  ├──┤ 1:M
            │ created_at     │  │
            └────────────────┘  │
                 │             │
     ┌───────────┴──────┐      │
     │                  │      │
┌────────────┐   ┌──────────────┐
│ CATEGORIES │   │    ISSUES    │
├────────────┤   ├──────────────┤
│ id (PK)    │   │ id (PK)      │
│ title (UQ) │   │ number       │
└────────────┘   │ publish_date │
                 └──────────────┘
```

### 3.2 Таблицы и поля

#### **1. authors** (Авторы статей)
```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);
```
- **id**: Первичный ключ, уникальный идентификатор
- **name**: ФИО автора (не пусто)
- **email**: Email автора (уникальный, не пусто)

#### **2. categories** (Категории статей)
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL
);
```
- **id**: Первичный ключ
- **title**: Название категории (уникальное, не пусто)

#### **3. issues** (Выпуски журнала)
```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    number INTEGER NOT NULL,
    publish_date DATE NOT NULL
);
```
- **id**: Первичный ключ
- **number**: Номер выпуска
- **publish_date**: Дата публикации

#### **4. articles** (Статьи)
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER FOREIGN KEY → authors(id),
    category_id INTEGER FOREIGN KEY → categories(id),
    issue_id INTEGER FOREIGN KEY → issues(id),
    created_at TIMESTAMP
);
```
- **id**: Первичный ключ
- **title**: Заголовок статьи (не пусто)
- **content**: Содержимое статьи (не пусто)
- **author_id**: Внешний ключ на авторов
- **category_id**: Внешний ключ на категории
- **issue_id**: Внешний ключ на выпуски
- **created_at**: Время создания

### 3.3 SQL Запросы с JOIN и GROUP BY

#### **Запрос 1: Статистика авторов**
```sql
SELECT
    authors.id,
    authors.name,
    authors.email,
    COUNT(articles.id) as article_count
FROM authors
LEFT JOIN articles ON authors.id = articles.author_id
GROUP BY authors.id, authors.name, authors.email;
```
**Назначение:** Показывает количество статей для каждого автора
**Вывод на странице:** `/statistics` → таблица "Статистика авторов"

#### **Запрос 2: Статистика категорий**
```sql
SELECT
    categories.id,
    categories.title,
    COUNT(articles.id) as article_count
FROM categories
LEFT JOIN articles ON categories.id = articles.category_id
GROUP BY categories.id, categories.title;
```
**Назначение:** Показывает количество статей в каждой категории
**Вывод:** `/statistics` → карточки "Статистика категорий"

#### **Запрос 3: Статистика выпусков (многоуровневый JOIN)**
```sql
SELECT
    issues.id,
    issues.number,
    issues.publish_date,
    COUNT(articles.id) as article_count,
    COUNT(DISTINCT authors.id) as unique_authors
FROM issues
LEFT JOIN articles ON issues.id = articles.issue_id
LEFT JOIN authors ON articles.author_id = authors.id
GROUP BY issues.id, issues.number, issues.publish_date
ORDER BY issues.publish_date DESC;
```
**Назначение:** Показывает количество статей и уникальных авторов для каждого выпуска
**Вывод:** `/statistics` → таблица "Статистика выпусков"

**Реализация в коде:**
```python
# database/crud.py
async def get_authors_with_article_count(db: AsyncSession):
    stmt = select(
        Author.id,
        Author.name,
        Author.email,
        func.count(Article.id).label('article_count')
    ).outerjoin(Article).group_by(Author.id, Author.name, Author.email)
    result = await db.execute(stmt)
    return result.all()
```

---

## 4. БАЗА ДАННЫХ MongoDB

### 4.1 Коллекции (2 коллекции)

#### **1. comments** (Комментарии к статьям)
```javascript
db.comments.insertOne({
    "_id": ObjectId("..."),
    "article_id": 1,
    "author": "Иван Петров",
    "text": "Отличная статья!",
    "rating": 5,
    "created_at": ISODate("2026-04-01T10:30:00Z")
})
```
**Назначение:** Хранение комментариев пользователей
**Поля:**
- `_id`: Уникальный идентификатор (MongoDB)
- `article_id`: ID статьи (связь с PostgreSQL)
- `author`: Имя автора комментария
- `text`: Текст комментария
- `rating`: Оценка 1-5
- `created_at`: Время создания

#### **2. statistics** (Глобальная статистика)
```javascript
db.statistics.insertOne({
    "_id": "global",
    "total_views": 1500,
    "total_comments": 245
})
```
**Назначение:** Хранение агрегированной статистики
**Поля:**
- `_id`: Идентификатор (фиксированное значение "global")
- `total_views`: Общее количество просмотров
- `total_comments`: Общее количество комментариев

### 4.2 MongoDB Запросы с агрегацией

#### **Запрос: Средний рейтинг комментариев к статье**
```javascript
db.comments.aggregate([
    { "$match": { "article_id": 1 } },
    { "$group": {
        "_id": "$article_id",
        "avg": { "$avg": "$rating" }
    }}
])
```
**Этапы конвейера:**
- `$match`: Фильтрует комментарии по article_id
- `$group`: Группирует по article_id и вычисляет средний рейтинг

**Реализация:**
```python
# utils.py
cursor = comments_col.aggregate([
    {"$match": {"article_id": article_id}},
    {"$group": {"_id": "$article_id", "avg": {"$avg": "$rating"}}}
])
stats = await cursor.to_list(1)
avg = stats[0]["avg"] if stats else 0
```

**Вывод на странице:**
- `/articles/{id}` → "Средний рейтинг"
- `/statistics` → глобальная статистика

---

## 5. КЕШИРОВАНИЕ Redis

### 5.1 Архитектура кеша

Redis используется для кеширования часто используемых данных:

```
Redis структуры:
├─ String: article:*:avg_rating = "4.5" (TTL: 3600 сек)
├─ String: comments:count:* = "45" (TTL: 7200 сек)
└─ Sorted Set: popular:articles = {article_id: view_count}
```

### 5.2 Реализованные ключи

#### **Ключ 1: article:{id}:avg_rating**
```python
# Тип: String
# Значение: Средний рейтинг статьи
# TTL: 3600 секунд (1 час)

cache_key = f"article:{article_id}:avg_rating"
await rd.setex(cache_key, 3600, str(avg))  # SET с expiration
```

**Процесс:**
1. Проверка Redis кеша
2. Если не найдено → вычисление из MongoDB с агрегацией
3. Сохранение в Redis с TTL 3600 сек
4. При добавлении комментария → инвалидация кеша (DELETE)

#### **Ключ 2: popular:articles**
```python
# Тип: Sorted Set (отсортированное множество)
# Значение: {article_id: view_count}
# TTL: не установлен (пока постоянный)

await rd.zincrby("popular:articles", 1, str(article_id))  # Increment score
await rd.zrevrange("popular:articles", 0, 9)  # Get top 10
```

**Процесс:**
1. Каждый просмотр статьи инкрементирует счетчик в Sorted Set
2. Страница `/popular` получает топ 10 из Redis за O(log N)
3. Вывод в реальном времени без доп. вычислений

### 5.3 Использование Redis в приложении

```python
# routes.py - Добавление просмотра
await rd.zincrby("popular:articles", 1, str(article_id))

# routes.py - Инвалидация кеша при комментарии
await rd.delete(f"article:{article_id}:avg_rating")

# routes.py - Получение популярных статей
top_list = await rd.zrevrange("popular:articles", 0, 9, withscores=True)

# utils.py - Кеширование рейтинга с TTL
await rd.setex(cache_key, 3600, str(avg))  # TTL: 1 час
```

---

## 6. ПРОЦЕСС ПРОЕКТИРОВАНИЯ БД

### 6.1 Этап 1: Определение сущностей

**Анализ предметной области:**
- Газета публикует стати в выпусках
- Каждая статья написана одним автором
- Статьи разбиты по категориям
- Чтатели могут оставлять комментарии
- Комментарии содержат оценку

**Выделены сущности:**
1. `Author` - автор статьи
2. `Category` - тематическая категория
3. `Issue` - выпуск журнала
4. `Article` - статья
5. `Comment` - комментарий

### 6.2 Этап 2: Определение связей

```
User просмотры

1:M связи:
- 1 Автор → M Статей
- 1 Категория → M Статей
- 1 Выпуск → M Статей
- 1 Статья → M Комментариев (в MongoDB)
```

### 6.3 Этап 3: Определение атрибутов

**Author:**
- id (INT, PK)
- name (VARCHAR, NOT NULL)
- email (VARCHAR, UNIQUE, NOT NULL)

**Category:**
- id (INT, PK)
- title (VARCHAR, UNIQUE, NOT NULL)

**Issue:**
- id (INT, PK)
- number (INT, NOT NULL) - номер выпуска
- publish_date (DATE, NOT NULL)

**Article:**
- id (INT, PK)
- title (VARCHAR(200), NOT NULL)
- content (TEXT, NOT NULL)
- author_id (INT, FK)
- category_id (INT, FK)
- issue_id (INT, FK)
- created_at (TIMESTAMP)

### 6.4 Этап 4: Нормализация (3NF)

**Проверка 1NF:**
- ✅ Все атрибуты атомарные (не составные)
- ✅ Нет повторяющихся групп

**Проверка 2NF:**
- ✅ В 1NF
- ✅ Все неключевые атрибуты зависят от полного ключа

**Проверка 3NF:**
- ✅ Во 2NF
- ✅ Нет транзитивных зависимостей
- ✅ Каждая таблица представляет одну сущность

**Пример:** `Article.author_id` → связь, а не дублирование данных автора

### 6.5 Этап 5: Выбор баз данных

| База | Назначение | Причина выбора |
|------|-----------|-----------------|
| **PostgreSQL** | Основные данные | ACID, нормализация, связи |
| **MongoDB** | Комментарии + статистика | Гибкость, масштабируемость, не требует схемы |
| **Redis** | Кеш, рейтинги, популярность | Производительность, TTL, Sorted Sets |

---

## 7. ЗАПУСК ПРИЛОЖЕНИЯ

### 7.1 Предварительные требования

```bash
# Установка переменных окружения (.env)
SQL_USER=postgres
SQL_PASSWORD=password
SQL_IP=localhost
SQL_PORT=5432
SQL_NAME=lab3_db

MONGO_NAME=lab3_mongo
MONGO_IP=localhost
MONGO_PORT=27017

REDIS_IP=localhost
REDIS_PORT=6379
REDIS_NAME=0
```

### 7.2 Установка зависимостей

```bash
pip install -r requirements.txt
```

### 7.3 Запуск сервера

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**URL:** http://localhost:8000

---

## 8. ДЕМОНСТРАЦИЯ ФУНКЦИОНАЛЬНОСТИ

### Сценарий 1: Просмотр комментариев с рейтингом

```
1. Пользователь открывает /articles/1
2. Запрос: SELECT * FROM articles WHERE id=1
3. Из Redis: GET article:1:avg_rating
4. Если нет → MongoDB aggregation: $match, $group, $avg
5. Результат: Средний рейтинг 4.5 звёзд
6. Кеширование в Redis на 3600 сек
```

### Сценарий 2: Просмотр популярных статей

```
1. Пользователь открывает /popular
2. Redis: ZREVRANGE popular:articles 0 9
3. Получение топ 10 за O(log N)
4. Вывод со счетчиком просмотров
```

### Сценарий 3: Статистика по авторам

```
1. Пользователь открывает /statistics
2. PostgreSQL запрос:
   SELECT author.*, COUNT(articles)
   FROM authors
   LEFT JOIN articles ON authors.id = articles.author_id
   GROUP BY authors.id
3. Вывод в таблице на странице
```

---

## 9. РЕЗУЛЬТАТЫ И ВЫВОДЫ

### 9.1 Выполненные требования

- ✅ **Часть 1:** Веб-приложение с 7 страницами, HTTP взаимодействие
- ✅ **Часть 2:** PostgreSQL с 4 таблицами, 3NF, PK/FK, ограничения
- ✅ **Часть 3:** MongoDB с 2 коллекциями (comments, statistics)
- ✅ **Часть 4:** Redis с 2 ключами (рейтинг + популярность)
- ✅ **Часть 5:** SQL запросы с JOIN/GROUP BY, MongoDB агрегация, Redis TTL

### 9.2 Ключевые особенности

1. **Гибридная архитектура БД**: каждая БД используется оптимально
2. **Производительность**: Redis кеширование, Sorted Sets для рейтинга
3. **Масштабируемость**: PostgreSQL + MongoDB, разделение данных
4. **Демонстрационная страница**: `/statistics` показывает все запросы

### 9.3 Практическое применение

- **PostgreSQL**: для структурированных данных с отношениями
- **MongoDB**: для неструктурированных данных (комментарии, статистика)
- **Redis**: для быстрого доступа и кеширования (TTL автоматическая очистка)

---

## 10. ПРИЛОЖЕНИЯ

### A. Схема БД в SQL

```sql
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    number INTEGER NOT NULL,
    publish_date DATE NOT NULL
);

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES authors(id),
    category_id INTEGER REFERENCES categories(id),
    issue_id INTEGER REFERENCES issues(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### B. Структура проекта

```
lab3/
├── main.py                 # Точка входа FastAPI
├── config.py              # Конфигурация БД
├── utils.py               # Вспомогательные функции
├── requirements.txt       # Зависимости Python
├── .env                   # Переменные окружения
│
├── api/
│   └── routes.py          # API endpoints и маршруты
│
├── database/
│   ├── models.py          # SQLAlchemy ORM модели
│   ├── sql_db.py          # PostgreSQL подключение
│   ├── mongo_db.py        # MongoDB подключение + коллекции
│   ├── redis_db.py        # Redis подключение
│   └── crud.py            # CRUD операции и запросы
│
├── schemas/
│   └── schemas.py         # Pydantic валидация данных
│
└── templates/
    ├── base.html          # Базовый шаблон с навигацией
    ├── index.html         # Главная (список статей)
    ├── article_detail.html    # Детали статьи + комментарии
    ├── add_article.html       # Форма добавления статьи
    ├── search.html            # Поиск и фильтрация
    ├── popular.html           # Популярные статьи (Redis)
    ├── authors.html           # Список авторов
    └── statistics.html        # Статистика (GROUP BY, JOIN, агрегация)
```

---

**Автор:** Студент
**Дата завершения:** 2026-04-01
**Статус:** ✅ Все требования выполнены
