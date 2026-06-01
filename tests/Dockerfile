FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest pytest-mock

COPY app ./app
COPY tests ./tests
COPY pytest.ini .
COPY scripts/wait_and_test.sh ./wait_and_test.sh
RUN chmod +x wait_and_test.sh

CMD ["./wait_and_test.sh"]