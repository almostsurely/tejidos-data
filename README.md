# Tejidos [![Build Status](https://travis-ci.org/almostsurely/tejidos-data.svg?branch=main)](https://travis-ci.org/almostsurely/tejidos-data)


## Run tests before pushing


```buildoutcfg
 python -m nose2
```

You should expect an output like:

```buildoutcfg
----------------------------------------------------------------------
Ran 15 tests in 0.038s

OK
```

## Pre-setup

Make sure that virtualization is activated

*hardware must be done in Bios (usually CPU options)
*Software must be done in 'Windows features' (tick Virtual machine platform and Windows subsystem for Linux), also make sure Hyper-V is enabled

Make sure that WSL2 is properly installed, it can no longer be automatically installed by docker.

https://docs.microsoft.com/de-de/windows/wsl/install-win10#step-4---download-the-linux-kernel-update-package

Change the EOL of the following files (can be done using notepad++ edit -> EOL conversion -> save)

.env.prod
.env.prod.db
entrypoint.sh

## Setup

Building the docker image is accomplished with the following command:

```
docker build -t tejidos-data/gdal:3.2-python3.8 .
```

The image will install all dependencies found in `requirements.txt`. Note that if a dependency is added, the image must be created again. To run [pylint](https://pypi.org/project/pylint/) [mypy](http://mypy-lang.org/) and [nose2](https://docs.nose2.io/en/latest/) inside the docker container run the following command:

```
docker run -v $(pwd):/var/task tejido /bin/bash /var/task/ run_before_push.sh
```
If all tests pass you should see output similar to this:

```
Success: no issues found in 4 source files

------------------------------------
Your code has been rated at 10.00/10

.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

This must be executed before pushing into the repository to prevent from breaking the continuous integration system.
