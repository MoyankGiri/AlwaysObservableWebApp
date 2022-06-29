kubectl replace --force -f grafana-datasource-config.yaml 
kubectl apply -f grafana.yaml  
kubectl apply -f grafana_svc.yaml

