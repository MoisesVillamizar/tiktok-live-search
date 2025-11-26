# 🎥 KP DIGITAL - TikTok Live Search

Monitor de transmisiones en vivo de TikTok usando TikAPI oficial. Búsqueda manual de streamers en vivo con interfaz web moderna.

## 🌟 Características

- **Búsqueda manual** de streamers en vivo por query
- **TikAPI oficial** (sin web scraping)
- **Interfaz moderna** con colores morado, rosado y blanco
- **Loader interactivo** que muestra el progreso en tiempo real
- **Base de datos SQLite** para almacenar histórico
- **Tabla completa** con información de streamers
- **Lista copyable** de usernames para uso directo
- **Sin scraping automático** - solo búsquedas manuales

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes)
- Credenciales de TikAPI: https://tikapi.io/

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <your-repo-url>
cd tiktok-live-monitor
```

### 2. Crear entorno virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` con tus credenciales:

```env
# TikAPI Configuration
TIKAPI_KEY=tu_api_key_aqui
TIKAPI_ACCOUNT_KEY=tu_account_key_aqui

# Database
DATABASE_URL=sqlite:///./tiktok_monitor.db

# Server
HOST=0.0.0.0
PORT=8000
```

## 🎮 Uso

### Opción 1: Modo Interactivo

```bash
./start.sh
```

### Opción 2: Modo Background

```bash
# Iniciar
./start-background.sh

# Ver estado
./status.sh

# Ver logs
tail -f tiktok_monitor.log

# Detener
./stop.sh
```

### Opción 3: Script de búsqueda por terminal

```bash
source venv/bin/activate
python Moi.py gaming
python Moi.py "bienvenido"
```

### Acceder a la aplicación

- **Interfaz web**: http://localhost:8000
- **Health check**: http://localhost:8000/health
- **API docs**: http://localhost:8000/docs

## 📡 API Endpoints

### POST `/api/search-live`

Buscar streamers en vivo por query

**Query params:**
- `query`: Término de búsqueda (ej: "gaming", "music")

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/search-live?query=gaming"
```

**Respuesta:**
```json
{
  "success": true,
  "query": "gaming",
  "total": 45,
  "streamers": ["username1", "username2", ...],
  "streamers_data": [...]
}
```

### GET `/api/streamers`

Obtener lista de streamers almacenados

**Query params:**
- `query`: Filtrar por query
- `is_live`: true/false
- `limit`: Número de resultados (default: 100)
- `offset`: Offset para paginación

### GET `/api/statistics`

Obtener estadísticas del sistema

**Query params:**
- `hours`: Estadísticas de las últimas N horas (default: 24)

### GET `/api/queries`

Obtener todas las queries únicas

### GET `/health`

Health check del servidor

## 🗂️ Estructura del Proyecto

```
tiktok-live-monitor/
├── main.py                    # Punto de entrada
├── Moi.py                     # Script de búsqueda por terminal
├── requirements.txt           # Dependencias
├── .env                      # Configuración (no incluido en git)
├── .gitignore               # Archivos ignorados
├── README.md                # Documentación
├── tiktok_monitor.db        # Base de datos (generada)
├── tiktok_monitor.log       # Logs (generado)
├── search.sh                # Wrapper script
├── start.sh                 # Iniciar en modo interactivo
├── start-background.sh      # Iniciar en background
├── stop.sh                  # Detener servicio
├── status.sh                # Ver estado
│
└── app/
    ├── models/
    │   └── database.py      # Modelos SQLAlchemy
    │
    ├── services/
    │   ├── tikapi_service.py  # Servicio TikAPI
    │   └── scraper.py         # Wrapper de compatibilidad
    │
    ├── api/
    │   ├── __init__.py
    │   └── routes.py          # Endpoints FastAPI
    │
    └── templates/
        └── search.html        # Interfaz web principal
```

## 🎨 Interfaz Web

La interfaz incluye:

- **Barra de búsqueda** con input morado y botón gradiente
- **Loader interactivo** con 4 pasos:
  1. Conectando con TikTok API
  2. Buscando transmisiones en vivo
  3. Obteniendo recomendaciones
  4. Procesando resultados
- **Estadísticas** con total de streamers y query
- **Tabla de streamers** con:
  - Username
  - Query
  - Estado (EN VIVO/Offline)
  - Veces Visto
  - Primera Vez
  - Última Vez
  - Acción (Ver Live)
- **Lista de usernames** copiable para uso directo

## 🎨 Paleta de Colores

- **Morado principal**: #8B5CF6
- **Rosado**: #EC4899
- **Blanco**: #FFFFFF
- **Fondo**: Gradiente morado → rosado

## ⚙️ Funcionamiento Técnico

### TikAPI Integration

1. Busca streamers con `user.live.search(query)`
2. Extrae room_ids de los resultados
3. Obtiene recomendaciones con `user.live.recommend(room_id)`
4. Limita a 5 rooms para rapidez (~1 minuto por búsqueda)
5. Elimina duplicados y devuelve usernames únicos

### Base de Datos

- **Tabla Streamers**:
  - username (único)
  - query
  - viewers
  - first_seen
  - last_seen
  - times_seen
  - is_live

- **Tabla ScanHistory**:
  - timestamp
  - query
  - streamers_found
  - success
  - error_message

## ⚠️ Consideraciones

1. **Rate Limiting**: TikAPI tiene límites de solicitudes. Si alcanzas el límite verás error 429.

2. **Velocidad**: Cada búsqueda tarda ~50-60 segundos (5 rooms × ~10 segundos cada uno).

3. **Uso ético**: Respeta los términos de servicio de TikAPI.

4. **Costos**: TikAPI es un servicio de pago. Verifica tu plan en https://tikapi.io/

## 🚀 Deployment

### 🐳 Docker Hub + Servidor VPS (Contabo/Hostinger)

**Método recomendado - Imagen ya construida en Docker Hub**

La aplicación está publicada en Docker Hub: **`moivillaz/tiktok-live-search:latest`**

Cada vez que haces push a `main`, GitHub Actions automáticamente construye y publica la imagen en Docker Hub.

#### 1. Configurar GitHub Secrets (Solo primera vez)

Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions, y agrega:

- `DOCKER_USERNAME`: Tu usuario de Docker Hub
- `DOCKER_PASSWORD`: Tu password o token de Docker Hub

#### 2. Requisitos en el servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose -y

# Agregar usuario al grupo docker (opcional)
sudo usermod -aG docker $USER
```

#### 3. Clonar repositorio en el servidor

```bash
# SSH al servidor
ssh user@tu-servidor.com

# Clonar repositorio (solo necesitas docker-compose.yml y .env)
git clone https://github.com/MoisesVillamizar/tiktok-live-search.git
cd tiktok-live-search
```

#### 4. Configurar variables de entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Agrega tus credenciales:
```env
TIKAPI_KEY=tu_api_key_real
TIKAPI_ACCOUNT_KEY=tu_account_key_real
```

#### 5. Desplegar con un comando

```bash
# Script automático de deployment
./deploy.sh
```

El script automáticamente:
- ✅ Verifica que exista `.env`
- ✅ Crea directorio de datos
- ✅ Detiene contenedores antiguos
- ✅ **Descarga última imagen de Docker Hub**
- ✅ Inicia el servicio
- ✅ Verifica que todo esté corriendo

#### 6. Actualizar a la última versión

Cuando hagas cambios y pushes a GitHub, la imagen se actualiza automáticamente en Docker Hub. Para actualizar tu servidor:

```bash
# En tu servidor, simplemente ejecuta:
./deploy.sh

# O manualmente:
docker-compose pull
docker-compose up -d
```

#### 7. Comandos útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Detener servicio
docker-compose down

# Reiniciar servicio
docker-compose restart

# Ver estado
docker-compose ps

# Actualizar a última versión
docker-compose pull && docker-compose up -d
```

#### 8. Configurar dominio y SSL

**Nginx con Let's Encrypt:**

```bash
# Instalar Nginx
sudo apt install nginx -y

# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Configurar Nginx
sudo nano /etc/nginx/sites-available/tiktok-monitor
```

Contenido del archivo:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/tiktok-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com
```

#### 9. Flujo de trabajo completo

```
1. Haces cambios en el código local
2. git push origin main
3. GitHub Actions construye imagen y la sube a Docker Hub
4. En tu servidor ejecutas: ./deploy.sh
5. El servidor descarga la última imagen y la despliega
```

### 🏗️ Construcción Local (Opcional)

Si prefieres construir la imagen localmente en lugar de usar Docker Hub:

```bash
# Usa el archivo docker-compose.build.yml
docker-compose -f docker-compose.build.yml build
docker-compose -f docker-compose.build.yml up -d
```

### Railway.app

**Para deployment rápido sin servidor propio**

1. Crea nuevo proyecto desde GitHub
2. Conecta el repositorio `tiktok-live-search`
3. Agrega variables de entorno:
   - `TIKAPI_KEY`
   - `TIKAPI_ACCOUNT_KEY`
4. Deploy automático

### Render.com

1. Crea un nuevo Web Service
2. Conecta tu repositorio
3. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
4. Agrega variables de entorno:
   - `TIKAPI_KEY`
   - `TIKAPI_ACCOUNT_KEY`
   - `PORT=8000`

### Heroku

```bash
# Instalar Heroku CLI
heroku create your-app-name
heroku config:set TIKAPI_KEY=your_key
heroku config:set TIKAPI_ACCOUNT_KEY=your_account_key
git push heroku main
```

## 📝 Variables de Entorno

| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| `TIKAPI_KEY` | API Key de TikAPI | Sí | - |
| `TIKAPI_ACCOUNT_KEY` | Account Key de TikAPI | Sí | - |
| `DATABASE_URL` | URL de base de datos | No | `sqlite:///./tiktok_monitor.db` |
| `HOST` | Host del servidor | No | `0.0.0.0` |
| `PORT` | Puerto del servidor | No | `8000` |

## 🔧 Scripts de Utilidad

- `./start.sh` - Iniciar servidor en modo interactivo
- `./start-background.sh` - Iniciar en background con PID
- `./stop.sh` - Detener servicio en background
- `./status.sh` - Ver estado del servicio
- `./search.sh <query>` - Búsqueda rápida por terminal

## 📊 Ejemplos de Uso

```bash
# Búsqueda por terminal
./search.sh gaming
./search.sh "maquillaje"

# Búsqueda por API
curl -X POST "http://localhost:8000/api/search-live?query=fitness"

# Ver streamers guardados
curl "http://localhost:8000/api/streamers?limit=50"

# Ver estadísticas
curl "http://localhost:8000/api/statistics?hours=24"
```

## 🐛 Troubleshooting

### Error 429 - Rate Limit

El límite de solicitudes de TikAPI ha sido alcanzado. Espera unos minutos o revisa tu plan.

### Error 401 - Unauthorized

Verifica que tus credenciales de TikAPI sean correctas en el archivo `.env`.

### Base de datos bloqueada

```bash
rm tiktok_monitor.db
# La base de datos se recreará automáticamente
```

### Ver logs en tiempo real

```bash
tail -f tiktok_monitor.log
```

## 📧 Soporte

Para problemas o preguntas:
1. Revisa `tiktok_monitor.log`
2. Verifica configuración en `.env`
3. Abre un issue en GitHub

## 📄 Licencia

Proyecto desarrollado por **KP DIGITAL** para uso interno.

---

Desarrollado con ❤️ por KP DIGITAL
