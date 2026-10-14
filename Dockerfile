FROM python:3.10-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY cells/ ./cells/
COPY synapses/ ./synapses/
COPY shunya_engine.py .

CMD ["python", "shunya_engine.py"]
