FROM lambgeo/lambda-gdal:3.2-python3.8

# Copy any local files to the package
COPY ./requirements.txt ${PACKAGE_PREFIX}/requirements.txt

RUN pip install -r ${PACKAGE_PREFIX}/requirements.txt


