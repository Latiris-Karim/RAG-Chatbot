FROM python:3.9

WORKDIR /RAGAPI

COPY ./requirements.txt /RAGAPI/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /RAGAPI/requirements.txt

COPY . /RAGAPI/

CMD ["fastapi", "run", "main.py", "--port", "8080"]
