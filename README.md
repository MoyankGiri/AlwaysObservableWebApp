# An always observable Blogging web-app
<p> This is a blogging web application application built as part of HPE CTY Program</p>

## Technologies Used
<ul>
<li>Python Flask Backend</li>
<li>JWT Authentication</li>
<li>Mongodb and mongoose ORM for database</li>
<li>GRPC and Protobuff</li>
<li>Docker for dockerization and Kubernetes for orchestration</li>
<li> Grafana,Prometheus and Alert-Manager for monitoring the app</li>
<li>Deployment on EC2 instance</li>
</ul>

## Architecture
<p>Attached below are both AWS Dockerized architecture on left and K8 orchestrated app on right</p>
<img src="https://user-images.githubusercontent.com/61751287/179968936-b0c8d0e3-10ba-4b03-b110-7e303771c3e2.png" alt="architecture">

## How to run it?
<ol>
<li> Run <code>minikube start</code> </li>
<li> Run <code>./prom_operator_start.sh</code>
<li> Run <code> ./force_upgrade_config.sh </code>
<li> Run <code> ./kubectlStart.sh </code>
<li> Run the various port_forwarding scripts </li>
<li> Run <code>python3 workloadSim.py</code> </li>
<li> Import grafana dashboard </li>
</ol>

## Contributors (in alphabetical order)
<ol>
<li> Chandradhar Rao </li>
<li> Moyank Giri </li>
</ol>
