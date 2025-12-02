
FROM python:3.12-slim as builder


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt



FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY . .


RUN groupadd -r app_group && useradd --no-log-init -r -g app_group app_user
RUN chown -R app_user:app_group /app

ENV PATH="/opt/venv/bin:$PATH"

USER app_user

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
