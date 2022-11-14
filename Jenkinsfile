pipeline {
    agent any
    environment {
        NGINX_DOCKERFILE_PATH = "${env.WORKSPACE}/nginx"
        API_DOCKERFILE_PATH = "${env.WORKSPACE}/backend"
        CLIENT_DOCKERFILE_PATH = "${env.WORKSPACE}/frontend"
    }
    stages {
        stage('Start') {
            steps {
                slackSend color: "good", message: "Build Started: ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
                withCredentials([file(credentialsId: 'compose-env', variable: 'compose')]) {
                    writeFile file: 'compose.env', text: readFile(compose)
                }
                withCredentials([string(credentialsId: 'filekey', variable: 'filekey')]) {
                    writeFile file: './backend/filekey.key', text: filekey
                }
            }
        }
        stage('Build Docker Images') {
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
                sh 'docker image prune -af'
            }
        }
        stage('Deploy to test') {
            steps {
                sh "${env.WORKSPACE}/deploy.sh test"
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
            script {
            echo 'Finished running pipeline... gonna cleanup'
            cleanWs()
            }
        }
        success {
            slackSend   color: 'good',
                        message:"Build was successful!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        unstable {
            slackSend   color: 'warning',
                        message:"Build is unstable!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        changed {
            slackSend   color: 'warning',
                        message:"Build was changed!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        failure {
            slackSend   color: 'danger',
                        failOnError:true, message:"Build failed!  - ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
    }
    
}