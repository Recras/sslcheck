FROM python:3.7-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY test.py .
ENTRYPOINT ["python", "-u", "test.py"]
