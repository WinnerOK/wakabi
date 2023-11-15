CREATE SCHEMA IF NOT EXISTS wakabi;

SET search_path TO wakabi;

CREATE TABLE IF NOT EXISTS users (
  tg_id int64 PRIMARY KEY,
  language_level varchar(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS words (
  id BIGSERIAL PRIMARY KEY,
  word VARCHAR(255) NOT NULL,
  language_level varchar(10) NULL,
  word_phonetics text null,
  definition text NULL,
  voice_url text NULL
);
create index words_word on words(word);


CREATE TABLE IF NOT EXISTS word_knowledge (
  id BIGSERIAL PRIMARY KEY,
  user_id int64 NOT NULL,
  word_id int64 NOT NULL,
  is_learned bool NOT NULL DEFAULT false,
  last_training TIMESTAMPTZ NULL,

  unique (user_id, word_id)
);

create index word_knowledge_user on word_knowledge(user_id);
create index word_knowledge_word on word_knowledge(user_id);
