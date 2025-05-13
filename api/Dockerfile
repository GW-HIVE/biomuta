FROM python:3.10.4

WORKDIR /app 

ENV FLASK_APP=biomuta
ENV FLASK_ENV=production 

COPY ./requirements.txt .
RUN pip install -r requirements.txt 

# copy wheel distribution and install it 
COPY ./dist/biomuta-1.0-py3-none-any.whl .
RUN pip install biomuta-1.0-py3-none-any.whl

COPY . .

ENTRYPOINT FLASK_APP=biomuta gunicorn -b :80 'biomuta:create_app()' --timeout 120 --graceful-timeout 60