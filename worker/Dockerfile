FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip freeze > requirements.lock
COPY main.py ./main.py
COPY start.sh ./start.sh
RUN chmod +x start.sh
CMD ["./start.sh"]
