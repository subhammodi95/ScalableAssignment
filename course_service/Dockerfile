FROM python:3.10
WORKDIR /app
COPY app.py .
RUN pip install flask pymongo flasgger
CMD ["python", "app.py"]