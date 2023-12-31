create table wakabi.user_tinder_session
(
  session_id bigserial primary key,
  user_id    bigint references wakabi.users (tg_id)
);

create table wakabi.tinder_session_queue
(
  id bigserial primary key,
  session_id bigint references wakabi.user_tinder_session (session_id) on delete cascade not null,
  word       VARCHAR(255),
  word_order int,
  unique (session_id, word)
);

create index tinder_session_queue_order on wakabi.tinder_session_queue (session_id, word_order);
