FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y gcc build-essential
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python setup.py build_ext --inplace

CMD ["python", "bot.py"]
