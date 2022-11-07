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
    JENKINS_BUILD_NUMBER="${BUILD_NUMBER}"
    REMOTE_DIR="/home/jenkins"
    FINAL_PROJECT_PATH="${REMOTE_DIR}/final-project"
    MYSQL_VOLUME="mysql-vol"
    BACKEND_NETWORK="backend"
    FRONTEND_NETWORK="frontend"
}

copy_compose_file() {
    scp -o StrictHostKeyChecking=no "${JENKINS_WORKSPACE}/docker-compose.yaml" "${machine}:${FINAL_PROJECT_PATH}/"
}

copy_compose_env_file() {
    scp -o StrictHostKeyChecking=no "${JENKINS_WORKSPACE}/compose.env" "${machine}:${FINAL_PROJECT_PATH}/"
}

copy_wait_for_script() {
    scp -o StrictHostKeyChecking=no "${JENKINS_WORKSPACE}/wait-for.sh" "${machine}:${FINAL_PROJECT_PATH}/"
}

create_env_file() {
    ssh "${machine}" "cd ${FINAL_PROJECT_PATH} && echo BUILD_NUMBER=${JENKINS_BUILD_NUMBER} > .env"
}

copy_files_to_remote_machine() {
    copy_compose_file
    copy_compose_env_file
    create_env_file
    copy_wait_for_script
}

copy_tests() {
    echo "Going to copy tests dir to TEST machine"
    ssh "${machine}" "mkdir -p ${FINAL_PROJECT_PATH}/tests"
    scp -o StrictHostKeyChecking=no -r "${JENKINS_WORKSPACE}/tests" "${machine}:${FINAL_PROJECT_PATH}/"
    echo "Copied tests dir!"
}

run_tests() {
    ssh "${machine}" "cd ${FINAL_PROJECT_PATH}/tests && source test.sh"
    echo "Finshed running test.sh"
}

deploy_to_prod() {
    echo "Deploying to prod..."
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

apply_docker_compose_test() {
    ssh "${machine}" "cd ${FINAL_PROJECT_PATH} && docker compose down --rmi all &> /dev/null && docker compose up -d --no-build"
}

deploy_to_test() {
    copy_tests
    apply_docker_compose_test
    run_tests
}

apply_docker_compose_prod() {
    echo 'test'
    # check if nginx & mysql are up - if not bring them up

    # bring other services up and remove old ones
    # docker compose rm -fsv
}

deploy_to_prod() {
    apply_docker_compose_prod
}

deploy() {
    ssh "${machine}" "mkdir -p ${REMOTE_DIR}/final-project"
    copy_files_to_remote_machine
    validate_compose_network_and_volume_on_remote_machine
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
