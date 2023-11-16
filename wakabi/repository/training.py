from textwrap import dedent

import asyncpg


async def get_word_by_user(
    conn: asyncpg.Connection, user_tg_id: int
) -> list[asyncpg.Record]:
    return await conn.fetch(
        dedent(
            """
            SELECT
                word,
                word_id
            FROM wakabi.word_knowledge
            JOIN wakabi.words
                ON word_knowledge.word_id = words.id
            WHERE word_knowledge.is_learned = false AND
                  word_knowledge.user_id = $1
            ORDER BY last_training ASC LIMIT 1;
            """,
        ),
        user_tg_id,
    )


async def get_definition_by_word_id(
    conn: asyncpg.Connection, word_id: int
) -> list[asyncpg.Record]:
    return await conn.fetch(
        dedent(
            """
            SELECT
                word,
                definition
            FROM wakabi.words
            WHERE words.id = $1;
            """,
        ),
        word_id,
    )


async def update_word_after_training_iteration(
    conn: asyncpg.Connection,
    user_tg_id: int,
    word_id: int,
    is_learned: bool,
) -> None:
    await conn.execute(
        dedent(
            """
            UPDATE wakabi.word_knowledge
            SET
                is_learned=$1,
                last_training=NOW()
            WHERE word_id = $2 AND
                  user_id = $3;
            """,
        ),
        is_learned,
        word_id,
        user_tg_id,
    )
