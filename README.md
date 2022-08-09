# An always observable Blogging web-app
<p> This is a blogging web application application built as part of Hewlett Packard Enterprise CTY Program</p>

## Features and Activity Diagrams
<ol>

<li>Authorization</li>
<img src="https://user-images.githubusercontent.com/61751287/183634435-8ad9ce10-0212-4c0e-a612-a0a7306eb728.png">

<li>Login</li>
<img src="https://user-images.githubusercontent.com/61751287/183634508-845383a0-37cf-4531-8cd0-332b28322553.png">

<li>Create Account</li>
<img src="https://user-images.githubusercontent.com/61751287/183634280-df450e74-af7d-44bd-b588-c34e585fc9c2.png">

<li>Creating a Post</li>
<img src="https://user-images.githubusercontent.com/61751287/183634042-7073f174-8ab5-4684-b02e-c714d24e3b0c.png">

<li>Fetch Recent Posts</li>
<img src="https://user-images.githubusercontent.com/61751287/183634662-71a58c2a-84d4-43c8-8dd2-d1476c0a83fc.png">

<li>Delete Post</li>
<img src="https://user-images.githubusercontent.com/61751287/183634752-554d0d76-6242-45ce-a974-a5fbc7d9edb8.png">

<li>Edit and Update post</li>
<img src="https://user-images.githubusercontent.com/61751287/183634828-3dcecd5f-4e4e-4e57-8a4d-a7820fe63f20.png">

</ol>

## Tech Stack
<ul>
<li>Python Flask Framework for Backend</li>
<li>JWT for Authentication</li>
<li>Mongodb and mongoose ORM for database</li>
<li>GRPC and Protobuff for intra-microservice communication and REST APIs for endpoints</li>
<li>Docker for dockerization and Kubernetes for orchestration</li>
<li>Grafana,Prometheus and Alert-Manager for monitoring the health of the web app</li>
<li>Deployment on an EC2 instance</li>
</ul>

## Architecture
<p>Attached below are both AWS Dockerized architecture on left and K8 orchestrated app on right</p>
<img src="https://user-images.githubusercontent.com/61751287/179968936-b0c8d0e3-10ba-4b03-b110-7e303771c3e2.png" alt="architecture">

##Instructions for local setup
<ol>
<li> Run <code>minikube start</code> in the minikube installed environment</li>
<li> Run <code>./prom_operator_start.sh</code> to install kube-prometheus stack via helm chart</li>
<li> Run <code> ./force_upgrade_config.sh </code> to update the config map </li>
<li> Run <code> ./kubectlStart.sh </code> to start the pods</li>
<li> Run the various port_forwarding scripts to access via webbrowser</li>
<li> The app is now running on <a href="localhost:3000">AlwaysObservablBloggingApp</a></li>
<li> Run <code>python3 workloadSim.py</code> to simulate API requests(workload) </li>
</ol>

## Useful Links
<ol>
<li><a href="">Deployed Webapp</li>
</ol>

## Contributors (in alphabetical order)
<ol>
<li> Chandradhar Rao </li>
<li> Moyank Giri </li>
</ol>
