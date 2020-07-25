sudo docker build -t injest_service:dev .
sudo docker run -p 8080:8080 --env-file="../.env" injest_service:dev
