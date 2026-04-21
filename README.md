# FastRetail AI - Clasificación Automática de Catálogo

Este proyecto implementa un sistema de clasificación automática de imágenes para una tienda de e-commerce utilizando **Visión Artificial** en la nube. Es un trabajo desarrollado para el curso de especialización en **IA y Big Data (MEDAC)**.

## 🚀 Características

- **Análisis Inteligente**: Integración con **Amazon Rekognition** para la detección de etiquetas en imágenes de productos.
- **Backend de Alto Rendimiento**: Desarrollado con **FastAPI** para una comunicación rápida y asíncrona.
- **Normalización de Imágenes**: Procesamiento con **Pillow** para soportar múltiples formatos (WebP, PNG, JPEG) y convertirlos automáticamente al estándar de Rekognition.
- **Persistencia de Datos**: Almacenamiento local mediante **SQLite** y almacenamiento en la nube con **Amazon S3**.
- **Interfaz Moderna**: Frontend limpio y funcional desarrollado con HTML5, CSS3 y Vanilla JavaScript.

## 🛠️ Requisitos Técnico

### Tecnologías Utilizadas
- Python 3.10+
- FastAPI
- Boto3 (AWS SDK)
- Pillow (Image Processing)
- SQLAlchemy (Database)
- Jinja2 (Templating)

### Infraestructura AWS
- **Amazon S3**: Almacenamiento de las imágenes del catálogo.
- **Amazon Rekognition**: Inferencia para la detección de etiquetas.
- **IAM (o AWS Academy)**: Gestión de credenciales mediante Access Key, Secret Key y Session Token.

## ⚙️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/fastretail-ai.git
   cd fastretail-ai
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   Crea un archivo llamado `.env` en la raíz del proyecto basándote en `.env.example`:
   ```env
   AWS_ACCESS_KEY_ID=tu_access_key
   AWS_SECRET_ACCESS_KEY=tu_secret_key
   AWS_SESSION_TOKEN=tu_session_token (opcional si usas cuenta normal)
   AWS_DEFAULT_REGION=us-east-1
   AWS_S3_BUCKET_NAME=tu-nombre-de-bucket
   ```

## 🖥️ Ejecución

Para iniciar el servidor de desarrollo:
```bash
uvicorn main:app --reload
```
Una vez iniciado, abre tu navegador en [http://127.0.0.1:8000](http://127.0.0.1:8000).

## 📄 Licencia

Este proyecto ha sido desarrollado con fines académicos para el programa de formación de MEDAC.
