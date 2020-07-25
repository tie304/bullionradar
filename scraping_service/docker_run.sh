sudo docker build -t scraping_service:dev .
sudo docker run --env-file="../.env" -it scraping_service:dev python main.py