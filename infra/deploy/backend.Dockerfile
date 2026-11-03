# Backend image: API, ingestion worker and brain worker share it; docker-compose.prod.yml or fly.toml
# picks the process. Build from the repo root: docker build -f infra/deploy/backend.Dockerfile .
FROM python:3.15-slim-bookworm@sha256:4e03260adeeebafccd084f3584e6b84823aba5651cfb53ef8a078ed441ddf9cd

WORKDIR /app
COPY contracts ./contracts
COPY backend/requirements ./backend/requirements
# constraints.txt pins every package, so a rebuild can't quietly pull in something new.
RUN pip install --no-cache-dir -c backend/requirements/constraints.txt -e ./contracts/python \
    -r backend/requirements/brain.txt -r backend/requirements/senses.txt
COPY backend/app ./backend/app
COPY backend/migrations ./backend/migrations
COPY infra/osm/data ./infra/osm/data

# documents must exist here: a new named volume takes its owner from the image, or PO PDFs can't be written.
RUN useradd --create-home relief && mkdir -p /data/documents && chown -R relief /data
USER relief
WORKDIR /app/backend
ENV HOME=/home/relief PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header", "--timeout-keep-alive", "75"]
