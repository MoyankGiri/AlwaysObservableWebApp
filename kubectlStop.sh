kubectl scale deploy commentmicroservice --replicas=0
kubectl scale deploy postmicroservice --replicas=0
kubectl scale deploy authmicroservice --replicas=0
kubectl scale deploy apigateway --replicas=0
kubectl scale deploy mongodb --replicas=0
