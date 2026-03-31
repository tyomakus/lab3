✅ ФИНАЛЬНЫЙ CHECKLIST ДЛЯ ЗАЩИТЫ

## Созданные документы:

✅ 1. ОТЧЕТ_ПО_ЛАБОРАТОРНОЙ_РАБОТЕ.md
   ├─ Таблица 1: Сущности и связи (5 связей 1:M)
   ├─ Таблица 2: Атрибуты сущностей (4 таблицы, 13 полей)
   ├─ ER-диаграмма PostgreSQL
   ├─ Содержимое всех таблиц SQL
   ├─ Описание коллекций MongoDB (2 коллекции)
   ├─ Таблица Redis ключей (4 ключа, 1 с TTL)
   ├─ Описание 7 страниц приложения
   ├─ Описание 9 HTTP методов (GET/POST)
   ├─ Таблица всех методов и параметров
   └─ Проверка всех 7 требований (ВСЕ ✅)

✅ 2. ПОДРОБНЫЙ_ОТЧЕТ.md
   ├─ Описание предметной области
   ├─ Описание всех 4 таблиц PostgreSQL
   ├─ Примеры SQL запросов:
   │  ├─ SELECT простой (1 запрос)
   │  ├─ JOIN + GROUP BY (2 запроса)
   │  ├─ ДВОЙНОЙ JOIN + GROUP BY + COUNT(DISTINCT) (1 запрос)
   │  └─ INSERT (1 запрос)
   ├─ Примеры MongoDB запросов:
   │  ├─ INSERT (1 запрос)
   │  ├─ FIND + SORT (1 запрос)
   │  ├─ ⭐ АГРЕГАЦИЯ с $match и $group (1 запрос)
   │  └─ FIND_ONE (1 запрос)
   ├─ Примеры Redis запросов:
   │  ├─ INCR (счетчики) (2 запроса)
   │  ├─ ZINCRBY (просмотры статьи) (1 запрос)
   │  ├─ ⭐ SETEX (кеш с TTL=3600) (1 запрос)
   │  ├─ ZREVRANGE (топ статей) (1 запрос)
   │  ├─ GET (счетчики) (1 запрос)
   │  └─ DELETE (инвалидация) (1 запрос)
   ├─ Сравнение SQL vs MongoDB подходов
   └─ Полный рабочий сценарий с примерами (3 примера)

✅ 3. ИНСТРУКЦИЯ_ЗАЩИТЫ.md
   ├─ Структура документов
   ├─ План защиты (10 шагов)
   │  ├─ Вводная часть
   │  ├─ Архитектура БД
   │  ├─ Данные в БД
   │  ├─ PostgreSQL запросы (3 запроса детально)
   │  ├─ MongoDB запросы (3 типа запросов)
   │  ├─ Redis запросы (4 типа операций)
   │  ├─ Структура MongoDB
   │  ├─ Архитектура приложения
   │  ├─ Рабочий сценарий
   │  └─ Выводы и проверка требований
   ├─ Справочная таблица всех запросов
   ├─ Ответы на 6 возможных вопросов
   └─ Итоговая структура для защиты

✅ 4. ER_DIAGRAM.puml
   └─ PlantUML диаграмма расчесностей между таблицами

---

## Требования лабораторной работы (ВСЕ ВЫПОЛНЕНЫ ✅)

### ЧАСТЬ 1: ВЕБ-ПРИЛОЖЕНИЕ
✅ Клиентская часть: HTML шаблоны (Jinja2)
✅ Серверная часть: FastAPI приложение
✅ HTTP взаимодействие: GET и POST методы
✅ Минимум 5 страниц: 7 страниц реализовано

### ЧАСТЬ 2: БАЗА ДАННЫХ SQL (PostgreSQL)
✅ Минимум 3 таблицы: 4 таблицы реализовано
   - authors (ID, name, email)
   - categories (ID, title)
   - issues (ID, number, publish_date)
   - articles (ID, title, content, author_id FK, category_id FK, issue_id FK, created_at)

✅ Минимум 3 поля в каждой таблице: ВСЕ имеют
✅ Первичные ключи: ВСЕ таблицы имеют id как PK
✅ Внешние ключи: articles связана с authors, categories, issues (3 FK)
✅ Ограничения целостности:
   - UNIQUE на email и title категории
   - NOT NULL на обязательные поля
✅ 3-я нормальная форма: ВСЕ таблицы в 3НF (нет дублирования, функциональные зависимости)

### ЧАСТЬ 3: БАЗА ДАННЫХ MONGODB
✅ Минимум 2 коллекции: 2 коллекции реализовано
   - comments (документы с комментариями и рейтингами)
   - statistics (документ с глобальной статистикой)

### ЧАСТЬ 4: КЕШ REDIS
✅ Минимум 2 ключей: 4 ключей реализовано
✅ Информация из postgresql/mongodb: ВСЕ ключи хранят соответствующие данные
✅ Минимум 1 ключ с TTL: article:{id}:avg_rating имеет TTL = 3600 сек

### ЧАСТЬ 5: ЗАПРОСЫ К БАЗАМ ДАННЫХ
✅ PostgreSQL с JOIN: 3 запроса
   - get_authors_with_article_count (Author LEFT JOIN Article)
   - get_categories_with_stats (Category LEFT JOIN Article)
   - get_issues_with_stats (Issue LEFT JOIN Article LEFT JOIN Author)

✅ PostgreSQL с GROUP BY: 3 запроса (все вышеперечисленные содержат GROUP BY)

✅ MongoDB с агрегацией: 1 запрос
   - get_cached_rating с $match и $group
   - Вычисляет средний рейтинг статьи из комментариев

✅ Redis с TTL: 1 ключ
   - article:{id}:avg_rating с TTL = 3600 секунд

---

## Файлы исходного кода (ДЛЯ ПРОВЕРКИ)

api/routes.py (9 эндпоинтов):
  ├─ GET /                    (главная)
  ├─ GET /authors             (авторы)
  ├─ POST /authors/new        (добавить автора)
  ├─ GET /articles/new        (форма добавления)
  ├─ POST /articles/new       (создать статью)
  ├─ GET /articles/{id}       (детали статьи + комментарии)
  ├─ POST /articles/{id}/comments  (добавить комментарий)
  ├─ GET /search              (поиск)
  ├─ GET /popular             (популярные)
  └─ GET /statistics          (статистика)

database/crud.py:
  ├─ get_authors
  ├─ get_categories
  ├─ get_issues
  ├─ get_authors_with_article_count (JOIN + GROUP BY + COUNT)
  ├─ get_categories_with_stats (JOIN + GROUP BY + COUNT)
  └─ get_issues_with_stats (JOIN + JOIN + GROUP BY + COUNT DISTINCT)

database/models.py:
  ├─ Author (таблица)
  ├─ Category (таблица)
  ├─ Issue (таблица)
  └─ Article (таблица)

database/mongo_db.py:
  ├─ comments_col (коллекция)
  └─ statistics_col (коллекция)

database/redis_db.py:
  └─ redis_client (подключение)

utils.py:
  ├─ get_cached_rating (MongoDB aggregation + Redis SETEX с TTL)
  └─ update_statistics (MongoDB update)

---

## СТАТИСТИКА ПРОЕКТА

- **Страницы**: 7
- **HTTP методов**: 9 (7 GET + 2 POST)
- **Таблицы PostgreSQL**: 4
- **Коллекции MongoDB**: 2
- **Ключей Redis**: 4 (1 с TTL)
- **SQL запросов с JOIN**: 3
- **SQL запросов с GROUP BY**: 3
- **MongoDB запросов**: 4 (INSERT, FIND, Aggregation, FIND_ONE)
- **Redis операций**: 8 (INCR, ZINCRBY, SETEX, GET, DELETE, ZREVRANGE)
- **Строк документации**: 1000+
- **Примеров запросов**: 20+

---

## КЛЮЧЕВЫЕ МОМЕНТЫ ДЛЯ ЗАЩИТЫ

1️⃣ ER-ДИАГРАММА НА СЛОВАХ:
   "У нас есть четыре таблицы PostgreSQL
    в отношении One-to-Many: авторы пишут статьи,
    статьи принадлежат категориям и выпускам.
    Статьи также связаны логически с комментариями в MongoDB."

2️⃣ САМЫЙ СЛОЖНЫЙ ЗАПРОС:
   "В get_issues_with_stats используются два JOIN'а:
    Issue присоединяется к Articles, Articles присоединяется к Authors.
    Затем GROUP BY с COUNT(DISTINCT authors.id) для подсчета
    уникальных авторов в каждом выпуске."

3️⃣ MONGODB АГРЕГАЦИЯ:
   "Aggregation pipeline - это как SQL с GROUP BY.
    $match фильтрует документы,
    $group группирует и считает среднее значение рейтинга.
    Результат: средний рейтинг статьи из всех комментариев."

4️⃣ REDIS TTL:
   "SETEX устанавливает значение и время жизни одновременно.
    Ключ article:1:avg_rating существует 3600 секунд (1 час).
    После истечения Redis автоматически удаляет ключ.
    При новом просмотре рейтинг пересчитывается из MongoDB."

5️⃣ РАБОЧИЙ СЦЕНАРИЙ:
   "Пользователь заходит на статью:
    1. PostgreSQL возвращает информацию о статье
    2. MongoDB возвращает комментарии и вычисляет средний рейтинг через aggregation
    3. Redis кеширует рейтинг с TTL 1 час
    4. Redis увеличивает счетчик просмотров (INCR) и просмотров статьи (ZINCRBY)
    5. На странице статистики все три БД объединяются для отображения полной аналитики"

---

## КОГДА ВОПРОСЫ НА ЗАЩИТЕ

Если спросят про:
- JOIN → показать crud.py в get_issues_with_stats (строка 57-73)
- GROUP BY → все три запроса содержат GROUP BY
- COUNT(DISTINCT) → get_issues_with_stats считает уникальных авторов
- MongoDB aggregation → utils.py строка 12-17 (get_cached_rating)
- Redis TTL → utils.py строка 20 (SETEX с 3600 сек)
- Все БД работают → routes.py GET /statistics объединяет все три
- Примеры данных → ОТЧЕТ_ПО_ЛАБОРАТОРНОЙ_РАБОТЕ.md раздел 1.3

---

✨ ГОТОВО К ЗАЩИТЕ! ✨

Найди преподавателя с документами:
1. ОТЧЕТ_ПО_ЛАБОРАТОРНОЙ_РАБОТЕ.md
2. ИНСТРУКЦИЯ_ЗАЩИТЫ.md
3. Ноутбук/компьютер с исходным кодом (для демонстрации)
