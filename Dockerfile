# Use AWS Lambda's official Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

# Set working directory inside container
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first to leverage caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your lambda_function.py into the image
COPY lambda_function.py .

# Command to run the handler
CMD ["lambda_function.lambda_handler"]
