from textwrap import dedent

import asyncpg


async def get_word_by_user(
    conn: asyncpg.Connection, tg_id: int
) -> list[asyncpg.Record]:
    return await conn.fetch(
        dedent(
            """
            select word, word_id from wakabi.word_knowledge
            join wakabi.words
                on word_knowledge.word_id = words.id
            where word_knowledge.user_id = $1 and word_knowledge.status = false
            order by last_training desc limit 1;
            """,
        ),
        tg_id,
    )
    # you can access data by record['id']       change it


async def get_definition_by_word_id(
    conn: asyncpg.Connection, word_id: int
) -> list[asyncpg.Record]:
    return await conn.fetch(
        dedent(
            """
            select word, definition from wakabi.words
            where words.word_id = $1;
            """,
        ),
        word_id,
    )
    # you can access data by record['id']       change it


async def update_word_after_train(
    conn: asyncpg.Connection,
    tg_id: int,
    word_id: int,
    status: bool,
) -> None:
    await conn.execute(
        "UPDATE wakabi.word_knowledge "
        "SET "
        "   status=$1,"
        "   last_training=NOW()"
        "WHERE word_id=$2 AND user_id=$3;",
        status,
        word_id,
        tg_id,
    )
