FROM python:3.8.5

WORKDIR /app

COPY requirements.txt . 

RUN pip install -r requirements.txt --no-cache-dir 

COPY . .

LABEL author="Beresnev Vladislav" version="1.0"

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 