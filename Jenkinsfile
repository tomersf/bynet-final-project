pipeline {
    agent any
    environment {
        NGINX_DOCKERFILE_PATH = "${env.WORKSPACE/nginx}"
        API_DOCKERFILE_PATH = "${env.WORKSPACE/backend}"
        CLIENT_DOCKERFILE_PATH = "${env.WORKSPACE/frontend}"
    }
    stages {
        stage('Build') {
            steps {
                echo 'Running build automation'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    nginx = docker.build("tomersf/bynet-nginx","${NGINX_DOCKERFILE_PATH}")
                    api = docker.build("tomersf/bynet-api","${API_DOCKERFILE_PATH}")
                    client = docker.build("tomersf/bynet-client","${CLIENT_DOCKERFILE_PATH}")
                }
            }
        }
        stage('Push Docker Images') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker_hub_login') {
                        api.push("${env.BUILD_NUMBER}")
                        api.push("latest")
                        nginx.push("${env.BUILD_NUMBER}")
                        nginx.push("latest")
                        client.push("${env.BUILD_NUMBER}")
                        client.push("latest")
                    }
                }
            }
        }
        stage('Deploy to test') {
            steps {
                milestone(1)
                steps {
                    sh "${env.WORKSPACE}/deploy.sh test"
                }
            }
        }

        stage('Deploy to prod') {
            steps {
                input 'Deploy to Production?'
                milestone(1)
                sh "${env.WORKSPACE}/deploy.sh prod"
            }
        }
    }
}