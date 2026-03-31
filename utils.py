from database.mongo_db import comments_col, statistics_col

async def get_cached_rating(article_id: int, rd):
    cache_key = f"article:{article_id}:avg_rating"

    # Проверяем кеш в Redis
    cached = await rd.get(cache_key)
    if cached is not None:
        return float(cached) if cached != "null" else 0

    # Если нет кеша — считаем средний рейтинг в MongoDB с агрегацией
    cursor = comments_col.aggregate([
        {"$match": {"article_id": article_id}},
        {"$group": {"_id": "$article_id", "avg": {"$avg": "$rating"}}}
    ])
    stats = await cursor.to_list(1)
    avg = stats[0]["avg"] if stats else 0

    # Кешируем в Redis с TTL (3600 секунд = 1 час)
    await rd.setex(cache_key, 3600, str(avg) if avg > 0 else "null")
    return avg


# Функция для обновления глобальной статистики в MongoDB
async def update_statistics(article_views: int = 0, comment_count: int = 0):
    await statistics_col.update_one(
        {"_id": "global"},
        {
            "$inc": {
                "total_views": article_views,
                "total_comments": comment_count
            }
        },
        upsert=True
    )
