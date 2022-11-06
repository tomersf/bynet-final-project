#!/bin/bash
set -ue

check_args() {
    machine=$1
    case "$machine" in
    "test") echo "Gonna deploy to TEST machine" ;;
    "prod") echo "Gonna deploy to PROD machine" ;;
    *)
        echo "ERROR! Got unknown argument ${machine}"
        echo "Usage is ./deploy.sh [prod | test]"
        exit 1
        ;;

    esac
}

copy_compose_file_to_remote_machine() {
    scp -o StrictHostKeyChecking=no docker-compose.yml "${REMOTE_USERNAME}"@"${REMOTE_MACHINE}":"${COMPOSE_FILE_PATH}"
}

deploy_to_test() {
    echo "Deploying to test..."
    ssh
    copy_compose_file_to_remote_machine
    exit 0
}

deploy_to_prod() {
    echo "Deploying to prod..."
    exit 0
}

deploy() {
    if [[ "$machine" == 'test' ]]; then
        deploy_to_test
    else
        deploy_to_prod
    fi
}
echo "Starting deploy script..."
check_args "$1"
echo "Passed args validation..."
deploy
