pipeline {
    agent any
    environment {
        NGINX_DOCKERFILE_PATH = "${env.WORKSPACE/nginx}"
        API_DOCKERFILE_PATH = "${env.WORKSPACE/backend}"
        CLIENT_DOCKERFILE_PATH = "${env.WORKSPACE/frontend}"
    }
    stages {
        stage('Start') {
            steps {
                echo "Starting build..."
                echo "ls"
                slackSend color: "good", message: "Build Started: ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
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
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-login') {
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
    post {
        always {
            echo 'Finished running pipeline... gonna cleanup'
            cleanWs()
        }
        success {
            slackSend color: 'good', message:"Build was successful!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        unstable {
            slackSend color: 'warning', message:"Build is unstable!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }

        changed {
            slackSend color: 'warning', message:"Build was changed!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }

        failure {
            slackSend color: 'danger', failOnError:true, message:"Build failed!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
    }
}