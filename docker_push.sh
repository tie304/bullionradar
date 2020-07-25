sudo docker build -t tylerhanson1/api_service ./api_service
sudo docker build -t tylerhanson1/injest_service ./injest_service
sudo docker build -t tylerhanson1/spot_price_service ./spot_price_service
sudo docker build -t tylerhanson1/scraping_service ./scraping_service

sudo docker push tylerhanson1/api_service
sudo docker push tylerhanson1/injest_service
sudo docker push tylerhanson1/spot_price_service
sudo docker push tylerhanson1/scraping_service