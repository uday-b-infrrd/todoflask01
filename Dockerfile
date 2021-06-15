# set base image
FROM python:3.7

# indicates the port on wich a container wll listen for connections
EXPOSE 5000
# set working directory in the container
WORKDIR /code

# copy the dependencies file to working directory
COPY requirements.txt /code

# install dependencies
RUN pip install -r requirements.txt

# ENV PYTHONPATH=".\env\Lib\site-packages"
# ENV PYTHONPATH=".\env\Lib"

# copy the content of the local app directory to the working directory
COPY . .

# command to run on container start
CMD python app.py
