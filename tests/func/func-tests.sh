#!/bin/bash -ex

main() {
    test_container_starts
}

test_container_starts() {
    _mkrepo() {
        docker run --rm -it "${IMAGE:-$1}" "$@"
    }

    _mkrepo version
    _mkrepo --help
}


[[ "${BASH_SOURCE[0]}" == "$0" ]] && {
    readonly IMAGE="${1?Image name for testing is missing}"
    shift || :
    echo "Testing image: $IMAGE"
    main "$@"
}
