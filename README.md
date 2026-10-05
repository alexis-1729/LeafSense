# LeafSense


1. Copy `.env.example` to `.env` and set unique, strong values for all five secrets.
   The image dimensions and normalization values must also match the CNN training
   and ONNX export pipeline.
2. Place `pest-cnn.onnx` and `labels.json` in `model_artifacts/`. The labels file
   must be either a JSON string array or an object with a string-array `labels`
   property. Labels are ordered to match the ONNX output classes.
3. The service reads the fixed input dimensions and NCHW/NHWC layout from the
   ONNX signature. If the model has dynamic spatial axes, set
   `MODEL_INPUT_WIDTH` and `MODEL_INPUT_HEIGHT`. Image values are divided by 255;
   adjust `MODEL_IMAGE_MEAN` and `MODEL_IMAGE_STD` to match training.
4. Set `MODEL_OUTPUT_ACTIVATION=probabilities` if the ONNX output already contains
   probabilities summing to 1, or `softmax` if it contains logits.
5. Build and start the stack:

   ```sh
   docker compose up -d --build
   docker compose ps
   ```

Before starting `auth` and `users`, create the ignored `secrets/` files for an RSA
signing key pair and shared internal-service token. The private key must never be
committed or mounted in `users`; only `auth` receives it. In a controlled local
development environment, generate a 3072-bit key pair and a random token with:

```sh
mkdir -m 0700 -p secrets
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out secrets/jwt_private.pem
openssl pkey -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
openssl rand -hex 32 > secrets/internal_service_token
chmod 0400 secrets/jwt_private.pem secrets/jwt_public.pem secrets/internal_service_token
```
Set `JWT_KEY_ID` to a new value when rotating the signing key and replace the public
key mounted in `users` at the same time. With this single-key setup, existing access
tokens will stop validating immediately after rotation, so clients must authenticate
again; a multi-key overlap is a later enhancement.

Only Traefik publishes host ports. PostgreSQL, Qdrant, and `analysis-service` are
attached only to the internal Docker network. The RAG API and worker also join a
non-published egress network so they can download the embedding model and call the
external LLM; restrict outbound destinations with host firewall or an egress proxy
in production. The Traefik dashboard is disabled.
The analysis container starts only when both model artifacts are present and valid;
its readiness endpoint remains unhealthy if model loading fails.

Auth routes are published through Traefik on the `websecure` entrypoint only.
Configure a trusted TLS certificate/domain before production use. The API provides
`POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, and
`GET /jwks.json`. Access JWTs use RS256 with issuer, audience, key ID, and a 15-minute
default expiry. Refresh tokens are random opaque values stored only as SHA-256
hashes; rotation and family revocation are transactional. `users-service` verifies
JWTs with the public key and restricts profile changes to the authenticated user.
The `POST /internal/users` endpoint is not routed by Traefik and additionally
requires the shared internal-service token. A pending registration is safe to retry:
the same credentials re-attempt idempotent profile provisioning.

RAG ingestion accepts administrator-authenticated requests at
`POST /rag/documents` (`multipart/form-data`: exactly one of `file` or `text`, plus
`pest_label`, `crop`, `source`, and `language`). Plain text, Markdown, and
text-based PDFs are supported for file uploads; both input modes are limited by
`MAX_DOCUMENT_BYTES` after UTF-8 encoding or file reading. The endpoint responds
`202` with a document ID; query status at `GET /rag/documents/{id}`. The separate
worker stores extracted text/status in `rag_db`, chunks text, computes normalized
multilingual embeddings locally, and upserts deterministic point IDs in Qdrant.
The model cache is persisted in the `model_cache` volume.
`DELETE /rag/documents/{id}` removes its vectors and record. Changing the embedding
model or vector dimension requires a new Qdrant collection and reindexing.

Authenticated users can submit `POST /rag/diagnose` with
`multipart/form-data` fields `image` (JPEG, PNG, or WEBP; limited by
`MAX_IMAGE_BYTES`) and optional `crop` and `language`, plus a Bearer access token.


The analysis API provides `GET /health/live`, `GET /health/ready`, `GET /v2/models`,
and `POST /v2/models/pest-cnn/infer`. The request body is JSON with an `image`
property containing standard base64-encoded image bytes (no data-URI prefix).
JPEG, PNG, and WEBP are accepted. The response contains `label`, `confidence`, and
`top_k`.

The `pgdata` and `qdrant_data` volumes persist across container recreation. Do not
use `docker compose down -v` unless intentionally deleting all persisted data.


