from database.mongo_db import comments_col

async def get_cached_rating(article_id: int, rd):
    cache_key = f"article:{article_id}:avg_rating"

    # Проверяем кеш в Redis
    cached = await rd.get(cache_key)
    if cached is not None:
        return float(cached) if cached != "null" else 0

    # Если нет кеша — считаем средний рейтинг в MongoDB
    cursor = comments_col.aggregate([
        {"$match": {"article_id": article_id}},
        {"$group": {"_id": "$article_id", "avg": {"$avg": "$rating"}}}
    ])
    stats = await cursor.to_list(1)
    avg = stats[0]["avg"] if stats else 0

    await rd.setex(cache_key, 3600, str(avg) if avg > 0 else "null")
    return avg