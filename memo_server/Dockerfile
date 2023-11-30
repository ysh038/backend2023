FROM python:3.9.6
COPY . .
RUN pip3 install -r requirements.txt
WORKDIR /
CMD ["python3", "-m","flask","--app","memo","run","--host=0.0.0.0", "--port=8000", "--debug"]
