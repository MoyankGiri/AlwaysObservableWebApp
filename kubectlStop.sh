kubectl scale deploy commentmicroservice --replicas=0
kubectl scale deploy postmicroservice --replicas=0
kubectl scale deploy authmicroservice --replicas=0
kubectl scale deploy apigateway --replicas=0
kubectl scale deploy authmongodb --replicas=0
kubectl scale deploy postmongodb --replicas=0
kubectl scale deploy commentmongodb --replicas=0

# kubectl scale deploy -n default --replicas=0 --all # if using different namespace use that instead of default