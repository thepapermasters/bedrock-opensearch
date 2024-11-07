# Use an official Python base image
FROM python:3.12-slim

  # Install dependencies
RUN apt-get update && apt-get install -y \
poppler-utils \
&& rm -rf /var/lib/apt/lists/*

  # Set the working directory
WORKDIR /app

# Copy all files from the src directory located one level above the Docker context
COPY ./src /app
ENV PYTHONPATH="${PYTHONPATH}:/app"
# Install any necessary Python packages (if requirements.txt exists)
RUN pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi


#  # Define the command to run your application
#CMD ["python", "app.py"]

##########
#@@ -0,0 +1,47 @@
## Define custom function directory
#ARG FUNCTION_DIR="/function"
#
#FROM python:3.12 as build-image
## Include global arg in this stage of the build
#ARG FUNCTION_DIR
## Set working directory to function root directory
#WORKDIR ${FUNCTION_DIR}
#COPY constants.py ${FUNCTION_DIR}
#
## Copy function code
#RUN mkdir -p ${FUNCTION_DIR}
#COPY requirements.txt .
#RUN pip install -r requirements.txt
#RUN pip install awslambdaric
#
#FROM build-image as bedrock
#
## Include global arg in this stage of the build
#ARG FUNCTION_DIR
#
## Copy in the built dependencies
#COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
#RUN cat AgentLambda.py| md5sum
#COPY AgentLambda.py ${FUNCTION_DIR}
#
## Set runtime interface client as default command for the container runtime
#ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
## Pass the name of the function handler as an argument to the runtime
#CMD [ "AgentLambda.main" ]
#
#FROM build-image as opensearch
#
## Include global arg in this stage of the build
#ARG FUNCTION_DIR
## Set working directory to function root directory
#
## Copy in the built dependencies
#COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
#COPY IngestionLambda.py ${FUNCTION_DIR}
#RUN apt-get update -y
#RUN apt-get install -y poppler-utils
#
## Set runtime interface client as default command for the container runtime
#ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
## Pass the name of the function handler as an argument to the runtime
#CMD [ "IngestionLambda.main" ]




