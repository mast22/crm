FROM python:3
ENV PYTHONBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
EXPOSE 8000
COPY . /code/
CMD ["uvicorn", "crm.asgi:application", "--reload", "--host", "0.0.0.0", "--port", "8000"]