# Usa una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos
COPY requirements.txt .

# Actualizar el sistema e instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    poppler-utils \
    wkhtmltopdf \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar locales en español
RUN locale-gen es_ES.UTF-8

# Establecer las variables de entorno para el idioma
ENV LANG=es_ES.UTF-8 \
    LANGUAGE=es_ES:es \
    LC_ALL=es_ES.UTF-8

# Instalar las dependencias de Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install  --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# El area de trabajo se cambia de propietario

RUN chown -R www-data:www-data /app

# Cambiar al usuario www-data
USER www-data

# Comando para iniciar la aplicación Flask con Gunicorn (def) 
CMD ["gunicorn", "-w", "3", "-k", "gevent", "-b", "0.0.0.0:5000", "--timeout", "120", "--log-level", "info", "app:app"]