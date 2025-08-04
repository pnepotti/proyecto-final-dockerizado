FROM python:3.10.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expone el puerto por defecto de Django
EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]