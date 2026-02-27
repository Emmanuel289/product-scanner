FROM public.ecr.aws/lambda/python:3.13
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY app.py .

CMD ["app.handler"]