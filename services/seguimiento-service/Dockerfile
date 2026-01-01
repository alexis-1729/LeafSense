#imagen
FROM python:3.11-slim

#estable el directorio
WORKDIR /app

#Copiar archivos necesarios
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#Copiar el resto del codigo
COPY ./app ./app

ENV PYTHONPATH=/app

#Comando para arrancar el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]