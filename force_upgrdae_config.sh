helm upgrade --force --reuse-values -f alertmanager-config.yaml prometheus prometheus-community/kube-prometheus-stack -n default