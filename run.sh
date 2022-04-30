#------------ only do the first time -----------------
# docker build -t apigateway -f .\app\Dockerfile . --progress=plain
# docker build -t commentmicroservice -f .\microservices\comments_svc\src\Dockerfile . --progress=plain
# docker build -t postmicroservice -f .\microservices\post_svc\src\Dockerfile . --progress=plain
# docker build -t authmicroservice -f .\microservices\auth_svc\src\Dockerfile . --progress=plain
# ------------------------------
sudo docker stop $(sudo docker ps -aq)
docker container prune -f # use only when required
docker image prune -f
docker-compose build
docker-compose up