import asyncio
import asyncpg
import json
import aiofiles

DATASET_SAMPLE_PATH = "wiki_sample"
BATCH_SIZE = 5

async def push_to_db(pool, terms, end_batch_num):
    values = []
    for term in terms:
        word = term['word']
        pos = term['pos']
        word_phonetics = term['sounds']['ipa'] if term['sounds'] and 'ipa' in term['sounds'] else None
        voice_url = term['sounds']['mp3_url'] if term['sounds'] and 'mp3_url' in term['sounds'] else None
        definition = []
        for sense in term['senses']:
            if 'glosses' in sense:
                definition.append("; ".join(["- " + gloss for gloss in sense['glosses']]))
        if definition:
            definition_str = "\n".join(definition)
            values.append([word, pos, word_phonetics, definition_str, voice_url])
    if values:
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    "insert into wakabi.words (word, pos, word_phonetics, definition, voice_url) values ($1, $2, $3, $4, $5)",
                    values,
                )
    print("done ", end_batch_num, " written ", len(values))


async def main():
    pool = await asyncpg.create_pool(
        # TODO: remove
        # dsn=f'postgres://postgres:QU6Srsl6UEEEGbWd@localhost:45432/postgres'
        dsn=f'postgres://postgres:some_password@localhost:45432/postgres'
    )
    async with asyncio.TaskGroup() as tg:
        terms = []
        try:
            async with aiofiles.open(DATASET_SAMPLE_PATH, 'r') as f:
                idx = 0
                async for line in f:
                    terms.append(json.loads(line))
                    if len(terms) == BATCH_SIZE:
                        tg.create_task(push_to_db(pool, terms, idx + 1))
                        terms = []
                    idx += 1
                if terms:
                    tg.create_task(push_to_db(pool, terms, idx + 1))
        except Exception as e:
            print(e)
    await pool.close()
    print("done")


if __name__ == '__main__':
    asyncio.run(main())
