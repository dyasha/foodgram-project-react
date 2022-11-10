FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt . 

RUN pip install -r requirements.txt --no-cache-dir 

COPY . .

# RUN apt update

# RUN apt-get -y install wkhtmltopdf

LABEL author="Beresnev Vladislav" version="1.0" 

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 