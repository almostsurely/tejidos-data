FROM lambgeo/lambda-gdal:3.2-python3.8

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
# Copy any local files to the package
COPY ./requirements.txt ${PACKAGE_PREFIX}/requirements.txt

RUN pip install -r ${PACKAGE_PREFIX}/requirements.txt


# copy project
COPY . /usr/src/app/