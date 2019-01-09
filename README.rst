=======
mkrepo
=======

.. image:: https://img.shields.io/travis/gbenhaim/mkrepo.svg
        :target: https://travis-ci.org/gbenhaim/mkrepo


Build Yum/DNF repositories from multiple sources


* Free software: Apache Software License 2.0


Features
--------

* Build Yum/DNF repositories from multiple sources.
* Cache RPMs from remote repositories in order to accelerate repo composition.
* Fine grained control on RPMs selection.

Credits
-------

* This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.
* This package builds the target repository using Repoman_
* This package uses Reposync_ for caching RPMs.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Repoman: https://github.com/oVirt/repoman
.. _Reposync: https://github.com/rpm-software-management/yum-utils
