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

set_vars() {
    JENKINS_WORKSPACE="${WORKSPACE}"
    REMOTE_DIR="/home/jenkins"
    MYSQL_VOLUME="mysql-vol"
    BACKEND_NETWORK="backend"
    FRONTEND_NETWORK="frontend"
}

copy_compose_file() {
    scp -o StrictHostKeyChecking=no "${JENKINS_WORKSPACE}/docker-compose.yaml" "${machine}:${REMOTE_DIR}/final-project/"
}

copy_compose_env_file() {
    scp -o StrictHostKeyChecking=no "${JENKINS_WORKSPACE}/compose.env" "${machine}:${REMOTE_DIR}/final-project/"
}

copy_wait_for_script() {
    scp -o StrictHostKeyChecking=no "${JENKINS_WORKSPACE}/wait-for.sh" "${machine}:${REMOTE_DIR}/final-project/"
}

copy_files_to_remote_machine() {
    copy_compose_file
    copy_compose_env_file
    copy_wait_for_script
}

deploy_to_test() {
    echo "Deploying to test..."
    copy_files
    exit 0
}

deploy_to_prod() {
    echo "Deploying to prod..."
    exit 0
}

create_docker_volumes_on_remote_machine() {
    echo "Creating volume: ${MYSQL_VOLUME}"
    ssh "${machine}" "docker volume create ${MYSQL_VOLUME}"
    echo "Passed volume creation"
}

create_docker_networks_on_remote_machine() {
    echo "Starting to check / create docker compose networks"
    ssh "${machine}" "docker network ls | grep ${BACKEND_NETWORK} > /dev/null || docker network create --driver bridge ${BACKEND_NETWORK} && echo created ${BACKEND_NETWORK} network"
    ssh "${machine}" "docker network ls | grep ${FRONTEND_NETWORK} > /dev/null || docker network create --driver bridge ${FRONTEND_NETWORK} && echo created ${BACKEND_NETWORK} network"
    echo "Passed networks check / creation"
}

validate_compose_network_and_volume_on_remote_machine() {
    create_docker_networks_on_remote_machine
    create_docker_volumes_on_remote_machine
}

validate_nginx_and_mysql_are_up() {

}

deploy() {
    ssh "${machine}" "mkdir -p ${REMOTE_DIR}/final-project"
    copy_files_to_remote_machine
    validate_compose_network_and_volume_on_remote_machine
    validate_nginx_and_mysql_are_up
    if [[ "$machine" == 'test' ]]; then
        deploy_to_test
    else
        deploy_to_prod
    fi
}

main() {
    echo "Starting deploy script..."
    check_args "$1"
    echo "Passed args validation..."
    echo "Starting to set local variables"
    set_vars
    echo "Passed setting variables"
    echo "Starting deplyoment to remote machine"
    deploy
    echo "Deployed successfully!"
}

main "$@"
