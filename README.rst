=======
mkrepo
=======

.. image:: https://travis-ci.com/gbenhaim/mkrepo.svg?branch=master
    :target: https://travis-ci.com/gbenhaim/mkrepo

.. image:: https://quay.io/repository/gbenhaim/mkrepo/status
    :target: https://quay.io/repository/gbenhaim/mkrepo

Build Yum/DNF repositories from multiple sources


* Free software: Apache Software License 2.0


Features
--------

* Build Yum/DNF repositories from multiple sources.
* Cache RPMs from remote repositories in order to accelerate repo composition.
* Fine grained control on RPMs selection.

Usage
-------
.. code-block:: bash

   $ docker run --rm  quay.io/gbenhaim/mkrepo:latest [OPTIONS] COMMAND [ARGS]...


*In order to keep persistent RPM cache,
or creating the target repo outside of the container, use Docker's `-v` option.*

Credits
-------

* This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.
* This package builds the target repository using Repoman_
* This package uses Reposync_ for caching RPMs.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Repoman: https://github.com/oVirt/repoman
.. _Reposync: https://github.com/rpm-software-management/yum-utils
