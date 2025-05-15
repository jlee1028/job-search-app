FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "main"]