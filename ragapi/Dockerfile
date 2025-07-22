FROM python:3.9

WORKDIR /ragapi

COPY ./requirements.txt /ragapi/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /ragapi/requirements.txt

COPY . /ragapi/

CMD ["fastapi", "run", "main.py", "--port", "8080"]
