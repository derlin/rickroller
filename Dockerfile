FROM python:3.9-alpine3.15

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY assets /app/assets
COPY templates /app/templates
COPY rickroller.py server.py /app/

ENTRYPOINT ["python", "/app/server.py"]