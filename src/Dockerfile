FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim
WORKDIR /app
RUN mkdir data
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . .
EXPOSE 80
#ENV DATABASE_PATH=/app/data/database
ENV DATABASE_URL="postgresql://test_user:test_password@localhost:5432/test_db" 
#postgresql://fcasadei:7IGc540zOTX04ET@mstorage-svc:5432/dataset_schema
CMD ["python", "main.py"]
