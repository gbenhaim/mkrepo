FROM centos:7.6.1810

RUN yum install -y epel-release \
    && yum install -y https://resources.ovirt.org/repos/ci-tools/el7/noarch/repoman-2.0.38-1.el7.centos.noarch.rpm \
    && yum install -y yum-utils \
    && yum install -y python2-pip \
    && yum install -y which \
    && yum clean all

COPY dist /dist
COPY requirements.txt.lock /requirements.txt.lock

RUN pip install -r requirements.txt.lock

RUN pip install /dist/mkrepo*.whl \
    && rm -r /dist requirements.txt.lock

ENTRYPOINT ["mkrepo"]
