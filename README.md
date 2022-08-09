# An always observable Blogging web-app
<p> This is a blogging web application application built as part of HPE CTY Program</p>

## Features and Activity Diagrams
<ol>
<li>Authorization</li>
<li>Login</li>
<Create Account</li>
<li>Creating a Post</li>
<li>Fetch Recent Posts</li>
<li>Delete Post<li>
<li>Edit and Update post</li>
</ol>

## Tech Stack
<ul>
<li>Python Flask Backend</li>
<li>JWT Authentication</li>
<li>Mongodb and mongoose ORM for database</li>
<li>GRPC and Protobuff</li>
<li>Docker for dockerization and Kubernetes for orchestration</li>
<li>Grafana,Prometheus and Alert-Manager for monitoring the app</li>
<li>Deployment on EC2 instance</li>
</ul>

## Architecture
<p>Attached below are both AWS Dockerized architecture on left and K8 orchestrated app on right</p>
<img src="https://user-images.githubusercontent.com/61751287/179968936-b0c8d0e3-10ba-4b03-b110-7e303771c3e2.png" alt="architecture">

##Instructions
<ol>
<li> Run <code>minikube start</code> in the minikube installed environment</li>
<li> Run <code>./prom_operator_start.sh</code> to install kube-prometheus stack via helm chart</li>
<li> Run <code> ./force_upgrade_config.sh </code> to update the config map </li>
<li> Run <code> ./kubectlStart.sh </code> to start the pods</li>
<li> Run the various port_forwarding scripts to access via webbrowser</li>
<li> Run <code>python3 workloadSim.py</code> to simulate API requests(workload) </li>
</ol>

## Useful Links
<ol>
<li>Deployed Webapp</li>
</ol>

## Contributors (in alphabetical order)
<ol>
<li> Chandradhar Rao </li>
<li> Moyank Giri </li>
</ol>
