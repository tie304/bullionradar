sudo docker build -t tylerhanson1/api_service:dev .
sudo docker run -p 80:80 --env-file="../.env" tylerhanson1/api_service:dev