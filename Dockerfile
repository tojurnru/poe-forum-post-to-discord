FROM python:3.9.2
RUN mkdir /blacklistUpdater
WORKDIR /blacklistUpdater
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
