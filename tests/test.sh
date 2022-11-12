#!/bin/bash
set -ue

make_request() {
    url=$1
    status=$(curl --head --location --connect-timeout 5 --write-out %{http_code} --silent --output /dev/null "${url}")
    if [[ $status == 500 ]] || [[ $status == 000 ]]; then
        echo "Failed making request to ${url}"
        return 1
    else
        echo "Success making request to ${url}"
        return 0
    fi
}

check_site_response() {
    local local_url=http://localhost
    if make_request $local_url; then
        local ip
        ip=$(curl -s "http://checkip.amazonaws.com")
        if make_request "$ip"; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

check_site_response
