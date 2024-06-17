FROM --platform=linux/amd64 python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN chmod -R 777 /app

EXPOSE 8080

CMD ["chainlit", "run", "app/app.py", "--port", "8080"]