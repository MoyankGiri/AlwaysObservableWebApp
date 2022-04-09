sudo docker stop $(sudo docker ps -aq)
docker container prune -f
docker image prune -f
docker-compose build
docker-compose up