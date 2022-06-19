FROM python:3.8

WORKDIR /code/data_collector

ENV PYTHONPATH "${PYTHONPATH}:/code/"
COPY ./requirements.txt code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./code/requirements.txt

COPY ./KanalServiceGoogle.json /code/data_collector/KanalServiceGoogle.json
COPY ./central_bank.py /code/data_collector/central_bank.py
COPY ./google_connection.py /code/data_collector/google_connection.py
COPY . /code/data_collector

CMD ["python3", "-u", "./main.py"]

