#!/bin/bash -ex

main() {
#    test_container_starts
    test_basic_sanity

    echo "Func tests: Success :)"
}


test_container_starts() {
    _mkrepo() {
        docker run --rm -it "${IMAGE:-$1}" "$@"
    }

    _mkrepo version
    _mkrepo --help
}

test_basic_sanity() {
	local root="$(realpath ${0%/*})"
	local fixtures="${root}/fixtures/test_basic_sanity"
    local sync_dir="$(mktemp -d)"
    local dest="$(mktemp -d)"
    local yum_config="${fixtures}/reposync-config.repo"
	local custom_source="${fixtures}/extra-sources.txt"
	local user="$(id -u)"

	_mkrepo() {
        docker run \
            --rm \
            -it \
            -v "${sync_dir}:${sync_dir}:rw" \
            -v "${dest}:${dest}:rw" \
            -v "${PWD}:${PWD}:rw" \
            "${IMAGE:-$1}" \
            "$@"
    }


	_createrepo() {
		docker run \
			--rm \
			-i \
			--entrypoint createrepo_c \
			-v "${PWD}:${PWD}:rw" \
			-u "$user" \
			"${IMAGE:-$1}" \
			"$@"
	}

	generate_config() {
		sed s,@ROOT@,"$PWD",g "$1" > "${1%.in}"
	}

	(
		cd "$fixtures"
		# Build dummy RPMs for the test
		docker run \
			--rm \
			-i  \
			-v "${PWD}/specs:/specs:rw" \
			-v "${PWD}/out:/out:rw" \
			-u "$user" \
			quay.io/gbenhaim/rpm-builder-el7 \
			/bin/bash -s < "build-rpms.sh"

		# Move the RPMs that we've built to their repo
		mv out/dummy-1.0.0-1.el7.x86_64.rpm out/foo-2.0.0-1.el7.x86_64.rpm repo-a
		mv out/dummy-2.0.0-1.el7.x86_64.rpm repo-b
		mv out/foo-1.0.0-1.el7.x86_64.rpm repo-c

		# Create repo metadate, mkrepo's container has createrepo, let's reuse it
		for suffix in a b c; do
			_createrepo "${PWD}/repo-${suffix}"
		done

		# Prepare configs for mkrepo
		generate_config reposync-config.repo.in
		generate_config extra-sources.txt.in

		_mkrepo \
        	-l debug \
        	reposetup \
        	--sync-dir "$sync_dir" \
        	--dest "$dest" \
        	--yum-config "$yum_config" \
			--custom-source "conf:${custom_source}"
	)

	# Assert that all file are in place
	[[ -d "${dest}/el7/repodata" ]] || {
        echo "Target repo doesn't have repodata dir"
        exit 1
    }

	for r in dummy-1.0.0-1.el7.x86_64.rpm foo-1.0.0-1.el7.x86_64.rpm; do
		[[ -e "${dest}/el7/x86_64/${r}" ]] && continue
		echo "Failed to find $r in the target repository"
		exit 1
	done
}


[[ "${BASH_SOURCE[0]}" == "$0" ]] && {
    readonly IMAGE="${1?Image name for testing is missing}"
    shift || :
    echo "Testing image: $IMAGE"
    main "$@"
}
