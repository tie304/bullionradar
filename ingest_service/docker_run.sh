sudo docker build -t ingest_service:dev .
sudo docker run -p 8080:8080 --env-file="../.env" ingest_service:dev
