import asyncpg


async def upsert_user_level(conn: asyncpg.Connection, tg_id: int, level: str):
    await conn.execute(
        "insert into wakabi.users (tg_id, language_level) "
        "VALUES ($1, $2) "
        "on conflict(tg_id) do update set language_level=excluded.language_level",
        tg_id,
        level,
    )
