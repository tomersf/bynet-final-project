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

copy_and_create_files_to_remote_machine() {
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
    echo "Going to run tests"
    local result
    result=$(ssh "${machine}" "cd ${FINAL_PROJECT_PATH}/tests && ./test.sh")
    if [[ $result == '0' ]]; then
        echo "Finshed running test.sh successfuly!"
    else
        echo "test.sh failed! please check if the site is up"
    fi
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
    ssh "${machine}" <<'EOF'
        docker network ls | grep ${BACKEND_NETWORK} > /dev/null || docker network create --driver bridge ${BACKEND_NETWORK} && echo created ${BACKEND_NETWORK} network
        docker network ls | grep ${FRONTEND_NETWORK} >/dev/null || docker network create --driver bridge ${FRONTEND_NETWORK} && echo created ${BACKEND_NETWORK} network
EOF
    # ssh "${machine}" "docker network ls | grep ${BACKEND_NETWORK} > /dev/null || docker network create --driver bridge ${BACKEND_NETWORK} && echo created ${BACKEND_NETWORK} network"
    # ssh "${machine}" "docker network ls | grep ${FRONTEND_NETWORK} > /dev/null || docker network create --driver bridge ${FRONTEND_NETWORK} && echo created ${BACKEND_NETWORK} network"
    echo "Passed networks check / creation"
}

validate_compose_network_and_volume_on_remote_machine() {
    create_docker_networks_on_remote_machine
    create_docker_volumes_on_remote_machine
}

apply_docker_compose_test() {
    echo "Going to bring down compose in TEST and bring up the up-to-date one"
    ssh "${machine}" "cd ${FINAL_PROJECT_PATH} && docker compose down --rmi all &> /dev/null && docker compose up -d --no-build"
    echo "SUCCESS! brought docker compose up in TEST"
}

deploy_to_test() {
    copy_tests
    apply_docker_compose_test
    run_tests
}

_modify_docker_compose_prod_helper_scale() {
    local container_names_arr=$1
    local replicas_count=$2
    for container_name in $container_names_arr; do
        local service_name
        service_name=$(echo "${container_name}" | awk -F "[-]" '{print $2}')
        echo "Going to scale service: ${service_name} to ${replicas_count} replicas"
        ssh "${machine}" "cd ${FINAL_PROJECT_PATH} && docker-compose up -d --scale ${service_name}=${replicas_count} --no-recreate"
        echo "SUCCESS! Service: ${service_name} was scaled to ${replicas_count} replicas"
    done
}

modify_docker_compose_prod_with_sleep() {
    # Need to get the current containers names in order to remove it after.
    local sleep_time=$1
    local container_names_arr
    # Only going to scale api & client - not updating nginx(will cause downtime in the current setup)
    container_names_arr=$(ssh "${machine}" docker ps -f "name=.*api|.*client" | awk '{print $NF}')

    # Scaling the relevant services, one container will be updated, one will be prev version.
    echo "Going to scale up services..."
    _modify_docker_compose_prod_helper_scale container_names_arr 2
    echo "Finished scaling up.. sleeping for ${sleep_time}s for spin up time"
    sleep "${sleep_time}"

    # Remove the service with the outdated version
    echo "Going to remove outdated containers & images..."
    for container_name in $container_names_arr; do
        echo "Going to remove container: ${container_name}"
        ssh "${machine}" "docker rm -f ${container_name}"
        echo "SUCCESS! Service: ${service_name} was scaled to ${replicas_count} replicas"
    done

    echo "Going to scale down services..."
    _modify_docker_compose_prod_helper_scale container_names_arr 1
    echo "Finished scaling down"

}

cleanup() {
    echo "Going to remove all stopped containers & unused/dangling images"
    ssh "${machine}" "docker container prune -f && docker image prune -af"
    echo "SUCCESS! Removed containers & images"
}

deploy_to_prod() {
    running_compose_projects_count=$(docker compose ls | wc -l | xargs)
    if [[ "$running_compose_projects_count" == '1' ]]; then
        # No running docker compose at all
        echo "No docker compose projects detected, going to run docker compose up in PROD"
        ssh "${machine}" "cd ${FINAL_PROJECT_PATH} && docker compose up -d --no-build"
    else
        # There is a running compose already
        echo "Detected already a running compose project, going to modify existing one"
        modify_docker_compose_prod_with_sleep 5
    fi

}

deploy() {
    ssh "${machine}" "mkdir -p ${REMOTE_DIR}/final-project"
    copy_and_create_files_to_remote_machine
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
    echo "Running cleanup func..."
    cleanup
    echo "Done running cleanup func..."
}

main "$@"
