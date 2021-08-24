This is my solution for task at **DevOps Internship Challenge 2021**

For build and start app on local host please ensure you have installed and running *docker* and *docker-compose* on your machine. Then clone this repo, cd to repo directory, and execute  
`docker-compose build`  
`docker-compose up -d`

For automated deploy i've used tiktalik service and it's api [tiktalik.com](https://tiktalik.com/)

Python3 script `./deploy_tiktalik/deploy.py` need at least two environmental variables   
`TIKTALIK_API_KEY` and `TIKTALIK_API_SECRET`. This should be written in file `./deploy_tiktalik/.env`  
Keys for tiktalik could be found at your tiktalik account. Please be aware that you need some funds on your account for using deploy script.     
# DevOps Internship Challenge 2021

Build and deploy application from **app** folder. Use whatever service or platform you want (AWS, Azure, GCP, bare metal and so on). Most of them have free tier option.
There are no bad solutions here. If you're stuck at some point, just describe what you think should be done. We want to see how you think and tackle the problems. Feel free to use whatever tools you want, in the end we want to see this application started somewhere.

Requirements:

1. Application must run as Docker container.
2. Create some basic CI/CD pipeline to build and deploy using Github Actions (or script to automate everything).
3. Push your code to the Github repository and send us a link.

**Nice to see:**
- deployed application publicly available

**Super nice to see:**
- deployment to some kind of Kubernetes cluster (hosted or locally started)