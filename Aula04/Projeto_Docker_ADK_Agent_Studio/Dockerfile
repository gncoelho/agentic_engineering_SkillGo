FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

WORKDIR /app

RUN python -m venv /opt/venv

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY agents ./agents
COPY services ./services
COPY shared ./shared

# O ADK Web é uma interface de desenvolvimento. O usuário sem privilégios
# também recebe permissão sobre o ambiente para os assets de runtime da UI.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app /opt/venv

USER appuser

EXPOSE 8000
EXPOSE 8001

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000", "/app/agents"]
