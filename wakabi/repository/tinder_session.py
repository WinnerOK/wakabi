from typing import Optional, Tuple

from textwrap import dedent

import asyncpg


async def start_session(
    conn: asyncpg.Connection,
    user_id: int,
    words: list[str],
) -> tuple[int, str]:
    session_id = await conn.fetchval(
        dedent(
            """
            insert into wakabi.user_tinder_session(user_id)
            values
            ($1)
            returning session_id
            """,
        ),
        user_id,
    )

    insert_data = [(session_id, w, idx) for idx, w in enumerate(words[1:])]
    await conn.executemany(
        dedent(
            """
            insert into wakabi.tinder_session_queue(session_id, word, word_order)
            values ($1, $2, $3)
            """,
        ),
        insert_data,
    )
    return session_id, words[0]


async def stop_session(conn: asyncpg.Connection, session_id: int):
    await conn.execute(
        dedent(
            """
            delete
            from wakabi.user_tinder_session
            where session_id = $1
            """,
        ),
        session_id,
    )


async def delete_word_from_session(
    conn: asyncpg.Connection,
    session_id: int,
    word: str,
):
    await conn.execute(
        dedent(
            """
            delete
            from wakabi.tinder_session_queue
            where session_id = $1 and word = $2
            """,
        ),
        session_id,
        word,
    )


async def get_next_word_from_session(
    conn: asyncpg.Connection,
    session_id: int,
) -> Optional[str]:
    return await conn.fetchval(
        dedent(
            """
            delete from wakabi.tinder_session_queue
            where id in (
                select id
                    from wakabi.tinder_session_queue
                    where session_id = $1
                    order by word_order
                    limit 1
                )
            returning word
            """,
        ),
        session_id,
    )
