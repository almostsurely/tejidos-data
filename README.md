# tejidos-data

First raster data examples are [here](https://www.dropbox.com/sh/fommmsz3g9fekyz/AAD0FNGvz6_T3KoyNLeLQwAKa?dl=0). 


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
