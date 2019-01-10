#!/bin/bash
set -ex

out_dir="/out"
mkdir -p "$out_dir"
topdir=$(mktemp -d)
rpmbuild -bb --define "_topdir $topdir" /specs/*.spec
find "$topdir" -iname "*.rpm" -exec mv {} "$out_dir" \;
