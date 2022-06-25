kubectl apply -f $(pwd)/app/Deployment.yml

for msvc in auth_svc post_svc comments_svc
do
    kubectl apply -f $(pwd)/microservices/$msvc/src/Deployment.yml
    kubectl apply -f $(pwd)/microservices/$msvc/src/MongoDeployment.yml
done

while ! kubectl port-forward svc/apigateway 5000
do
    echo "\nWaiting for pod creation..."
    sleep 10
done
