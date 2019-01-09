#!/bin/bash -ex

yum install -y epel-release
yum install -y https://resources.ovirt.org/repos/ci-tools/el7/noarch/repoman-2.0.38-1.el7.centos.noarch.rpm
yum install -y yum-utils
yum install -y python2-pip
