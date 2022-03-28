FROM python:3.9-alpine3.15

# caching of dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY setup.py /app/
COPY rickroll /app/rickroll
RUN pip install -e /app

ENTRYPOINT ["python", "-m", "rickroll"]