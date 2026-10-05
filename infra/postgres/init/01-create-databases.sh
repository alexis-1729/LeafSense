#!/bin/sh
set -eu

: "${AUTH_DB_PASSWORD:?AUTH_DB_PASSWORD is required}"
: "${USERS_DB_PASSWORD:?USERS_DB_PASSWORD is required}"
: "${RAG_DB_PASSWORD:?RAG_DB_PASSWORD is required}"

psql \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 \
  --set=auth_password="$AUTH_DB_PASSWORD" \
  --set=users_password="$USERS_DB_PASSWORD" \
  --set=rag_password="$RAG_DB_PASSWORD" <<'SQL'
CREATE ROLE auth_app LOGIN PASSWORD :'auth_password';
CREATE DATABASE auth_db OWNER auth_app;
REVOKE ALL ON DATABASE auth_db FROM PUBLIC;

CREATE ROLE users_app LOGIN PASSWORD :'users_password';
CREATE DATABASE users_db OWNER users_app;
REVOKE ALL ON DATABASE users_db FROM PUBLIC;

CREATE ROLE rag_app LOGIN PASSWORD :'rag_password';
CREATE DATABASE rag_db OWNER rag_app;
REVOKE ALL ON DATABASE rag_db FROM PUBLIC;
SQL
