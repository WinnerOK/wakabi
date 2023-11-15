from textwrap import dedent

import asyncpg


async def upsert_user_level(conn: asyncpg.Connection, tg_id: int, level: str):
    await conn.execute(
        "insert into wakabi.users (tg_id, language_level) "
        "VALUES ($1, $2) "
        "on conflict(tg_id) do update set language_level=excluded.language_level",
        tg_id,
        level,
    )


async def get_known_words(conn: asyncpg.Connection, tg_id: int) -> list[asyncpg.Record]:
    return await conn.fetch(
        dedent(
            """
            select distinct w.word, w.id
            from wakabi.words w
                left join wakabi.word_knowledge wk on w.id = wk.word_id and wk.user_id=$1
            where
               wk.word_id is not null or w.language_level <= (select language_level from wakabi.users where tg_id=$1)
            ;
            """,
        ),
        tg_id,
    )
    # you can access data by record['id']
