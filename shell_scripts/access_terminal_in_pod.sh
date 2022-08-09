#$1 - <pod name>: alertmanager-prometheus-kube-prometheus-alertmanager-0

#file of alert-manager.yaml:cat /etc/alertmanager/alertmanager.yml

kubectl exec -it -n default $1 /bin/sh

