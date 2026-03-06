FROM public.ecr.aws/lambda/python:3.13

# Copy the app code to the Lambda task root directory (/var/task/)
COPY app ${LAMBDA_TASK_ROOT}

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Set the CMD to the name of the handler function
CMD ["handler.handler"]
