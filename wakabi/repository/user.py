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
            select w.word
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


async def add_words_to_learn(conn: asyncpg.Connection, user_id: int, words: list[str]):
    await conn.execute(
        dedent(
            """
            insert into wakabi.word_knowledge(user_id, word_id)
            select $1 as user_id, w.id as word_id
            from wakabi.words w
            where w.word in $2;
            """
        ),
        user_id,
        words,
    )
