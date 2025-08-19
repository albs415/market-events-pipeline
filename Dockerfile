FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY etl ./etl
COPY .env.example ./.env.example
COPY README.md ./README.md
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "etl.main"]
