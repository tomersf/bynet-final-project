#!/bin/bash

check_args() {
    machine=$1
    case "$machine" in
    "test") echo "Gonna deploy to TEST machine" ;;
    "prod") echo "Gonna deploy to PROD machine" ;;
    *)
        echo "ERROR! Got unknown argument ${machine}"
        exit 1
        ;;

    esac
}

echo "Starting deploy script"
check_args "$1"
