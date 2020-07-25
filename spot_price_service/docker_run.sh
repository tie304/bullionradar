sudo docker build -t spot_price_service .
sudo docker run --env-file="../.env" -it spot_price_service:dev python main.py