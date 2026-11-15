FROM python:3.12-slim

WORKDIR /app

# poppler-utils fornece pdftotext/pdftoppm, usados por app/tools/extrair_enade.py
# para importar questoes de provas do ENADE a partir de PDF.
RUN apt-get update \
    && apt-get install -y --no-install-recommends poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
