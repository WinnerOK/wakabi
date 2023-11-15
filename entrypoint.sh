#!/usr/bin/env bash
set -e

pgmigrate \
    -c "host=localhost port=$PG_PORT dbname=$PG_DATABASE user=$PG_USER password=$PG_PASSWORD target_session_attrs=read-write" \
    -d $PG_DATABASE \
    -t latest \
    -v \
migrate

python wakabi/run.py
# CMD ["python", "-m", "wakabi.example"]
