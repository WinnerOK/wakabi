from textwrap import dedent

import asyncpg


async def get_word_by_user(
    conn: asyncpg.Connection,
    user_tg_id: int,
    order: str,
) -> list[asyncpg.Record]:
    return await conn.fetch(
        dedent(
            """
            SELECT
                word,
                word_id,
                pos
            FROM wakabi.word_knowledge
            JOIN wakabi.words
                ON word_knowledge.word_id = words.id
            WHERE word_knowledge.is_learned = false AND
                  word_knowledge.user_id = $1
            ORDER BY true_count {order}, random()
            LIMIT 1;
            """,
        ).format(order=order),
        user_tg_id,
    )


async def get_definition_by_word_id(
    conn: asyncpg.Connection,
    word_id: int,
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
    user_knows_the_word: bool,
) -> None:
    true_count_diff = 1 if user_knows_the_word else 0
    # FIXME: why didn't we do proper table normalization
    await conn.execute(
        dedent(
            """
            UPDATE wakabi.word_knowledge
            SET
                true_count=true_count+$3,
                last_training=NOW(),
                is_learned = (CASE
                    WHEN (true_count+$3) > 3 THEN true
                    ELSE false
                    END)
            WHERE user_id = $2 AND
            word_id = $1
            ;
            """,
        ),
        word_id,
        user_tg_id,
        true_count_diff,
    )
