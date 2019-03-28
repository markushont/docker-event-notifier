FROM python:3.7-alpine
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
WORKDIR /app
COPY /app/* /app/
CMD python main.py