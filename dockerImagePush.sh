



# $1->account name
# $2-> reponame

docker tag commentmicroservice $1/$2:commentmicroservice
docker push $1/$2:commentmicroservice
docker tag apigateway $1/$2:apigateway
docker push $1/$2:apigateway
docker tag postmicroservice $1/$2:postmicroservice
docker push $1/$2:postmicroservice
docker tag authmicroservice $1/$2:authmicroservice
docker push $1/$2:authmicroservice