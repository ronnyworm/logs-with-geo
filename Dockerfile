FROM python:3.13

RUN pip install pyinstaller

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt && pyinstaller --onefile main.py
