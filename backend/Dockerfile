FROM python:3.12-slim

WORKDIR /app

# Evita gerar .pyc e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências do sistema (opcional)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primeiro (cache)
COPY /backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY /backend .

EXPOSE 1337

# Produção
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1337", "--workers", "2"]