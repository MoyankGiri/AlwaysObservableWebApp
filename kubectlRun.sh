kubectl apply -f $(pwd)/app/Deployment.yml

for msvc in auth_svc post_svc comments_svc
do
    kubectl apply -f $(pwd)/microservices/$msvc/src/Deployment.yml
    kubectl apply -f $(pwd)/microservices/$msvc/src/MongoDeployment.yml
done

kubectl apply -f $(pwd)/microservices/auth_svc/src/AuthPodMonitor.yaml
kubectl apply -f $(pwd)/microservices/post_svc/src/PostPodMonitor.yaml
kubectl apply -f $(pwd)/app/AppServiceMonitor.yml

while ! kubectl port-forward svc/apigateway 5000
do
    echo "\nWaiting for pod creation..."
    sleep 10
done

#kubectl port-forward grafana-5f9587668c-g6c54 3000:3000
