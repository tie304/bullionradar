sudo docker build -t tylerhanson1/api_service ./api_service
sudo docker build -t tylerhanson1/ingest_service ./injest_service
sudo docker build -t tylerhanson1/spot_price_service ./spot_price_service
sudo docker build -t tylerhanson1/scraping_service ./scraping_service
sudo docker build -t tylerhanson1/aggregation_service ./aggregation_service
sudo docker build -t tylerhanson1/crawling_service ./crawling_service
sudo docker build -t tylerhanson1/data_processing_service ./data_processing_service

sudo docker push tylerhanson1/api_service
sudo docker push tylerhanson1/injest_service
sudo docker push tylerhanson1/spot_price_service
sudo docker push tylerhanson1/scraping_service
sudo docker push tylerhanson1/aggregation_service
sudo docker push tylerhanson1/crawling_service
sudo docker push tylerhanson1/data_processing_service