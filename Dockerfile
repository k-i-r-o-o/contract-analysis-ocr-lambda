FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lambda_function/ lambda_function/
COPY main.py .
COPY test_event.json .

CMD ["lambda_function.handler.lambda_handler"]
