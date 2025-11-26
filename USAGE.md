# 📘 Guía de Uso - TikTok Live Monitor

## 🔴 Búsqueda de Streamers en Vivo

### Opción 1: Script de Terminal

El script `search_live.py` te permite buscar streamers en vivo y ver los resultados directamente en la terminal.

#### Uso Básico:

```bash
# Usando el wrapper (más fácil)
./search.sh gaming

# O directamente con Python
source venv/bin/activate
python search_live.py gaming

# Sin argumentos usa "maquillaje" por defecto
./search.sh
```

#### Ejemplo de Salida:

```
======================================================================
🔴 TikTok Live Streamer Search
======================================================================

🔍 Buscando streamers en vivo con query: 'gaming'
----------------------------------------------------------------------

1️⃣ Buscando transmisiones en vivo...

📋 Streamers de búsqueda directa:
  📺 @soyalexa__
  📺 @creative.sergii
  📺 @hector.awm
  ...

🏠 Encontrados 18 rooms para obtener recomendaciones

2️⃣ Obteniendo streamers recomendados...

======================================================================
✅ RESULTADO FINAL: 62 streamers únicos encontrados
======================================================================
  1. @soyalexa__
  2. @creative.sergii
  3. @hector.awm
  ...

======================================================================
📊 Estadísticas:
   - Búsqueda directa: 18 streamers
   - Recomendados: 72 streamers
   - Total único: 62 streamers
======================================================================
```

### Opción 2: Interfaz Web

Accede a la interfaz web de búsqueda en tiempo real:

1. **Inicia el servidor** (si no está corriendo):
   ```bash
   ./start-background.sh
   ```

2. **Abre tu navegador** y visita:
   ```
   http://localhost:8000/search
   ```

3. **Ingresa tu query** (ej: "gaming", "music", "cooking") y haz clic en "🔍 Buscar"

4. **Ver resultados**:
   - Lista de todos los streamers encontrados
   - Links directos a sus perfiles
   - Estadísticas en tiempo real

### Opción 3: API REST

Puedes usar la API directamente desde tu código o con curl:

```bash
# Buscar streamers
curl -X POST "http://localhost:8000/api/search-live?query=gaming"
```

Respuesta:
```json
{
  "success": true,
  "query": "gaming",
  "total": 62,
  "streamers": [
    "soyalexa__",
    "creative.sergii",
    "hector.awm",
    ...
  ]
}
```

## 🚀 Comandos Rápidos

### Iniciar Servicios

```bash
# Modo interactivo (ver logs en pantalla)
./start.sh

# Modo background (como servicio)
./start-background.sh

# Ver estado
./status.sh

# Ver logs
tail -f tiktok_monitor.log
```

### Detener Servicios

```bash
# Detener servicio en background
./stop.sh

# O presiona Ctrl+C si está en modo interactivo
```

### Búsqueda Rápida

```bash
# Buscar streamers de gaming
./search.sh gaming

# Buscar streamers de música
./search.sh music

# Buscar streamers de cocina
./search.sh cooking
```

## 📊 URLs del Sistema

| Servicio | URL |
|----------|-----|
| **Monitor Principal** | http://localhost:8000 |
| **Búsqueda Live** | http://localhost:8000/search |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |
| **WebSocket** | ws://localhost:8000/ws |

## 🔧 Configuración

### Cambiar Query de Búsqueda Automática

Edita `.env`:

```env
SEARCH_QUERIES=gaming,music,cooking,art,fitness
```

### Cambiar Intervalo de Scraping

```env
SCRAPE_INTERVAL_MINUTES=5
```

### Cambiar Puerto

```env
PORT=8000
```

## 💡 Tips

### 1. Búsquedas Múltiples

Puedes ejecutar múltiples búsquedas en paralelo:

```bash
# Terminal 1
./search.sh gaming

# Terminal 2
./search.sh music

# Terminal 3
./search.sh cooking
```

### 2. Guardar Resultados

```bash
# Guardar en archivo
./search.sh gaming > gaming_streamers.txt

# Ver resultados guardados
cat gaming_streamers.txt
```

### 3. Filtrar Resultados

```bash
# Solo los usernames
./search.sh gaming | grep "📺" | awk '{print $2}'

# Contar resultados
./search.sh gaming | grep "📺" | wc -l
```

### 4. Monitoreo Continuo

```bash
# Buscar cada 5 minutos
watch -n 300 './search.sh gaming'
```

## 🐛 Troubleshooting

### Script no encuentra credenciales

```bash
# Verifica que .env existe
cat .env

# Verifica las variables
echo $TIKAPI_KEY
```

### Error 401 (Credenciales inválidas)

```bash
# Actualiza tus credenciales en .env
nano .env

# Verifica con el script
./search.sh test
```

### Puerto ocupado

```bash
# Cambiar puerto en .env
PORT=8080

# O detener proceso existente
./stop.sh
```

## 📝 Ejemplos de Uso

### Ejemplo 1: Encontrar streamers de un juego específico

```bash
./search.sh "valorant"
./search.sh "minecraft"
./search.sh "fortnite"
```

### Ejemplo 2: Buscar en diferentes idiomas

```bash
./search.sh "gaming"     # Inglés
./search.sh "juegos"     # Español
./search.sh "jogos"      # Portugués
```

### Ejemplo 3: Temas específicos

```bash
./search.sh "makeup"
./search.sh "fitness"
./search.sh "cooking"
./search.sh "asmr"
```

## 🎯 Casos de Uso

### 1. Investigación de Mercado
- Encuentra influencers en tu nicho
- Analiza tendencias de contenido
- Identifica colaboradores potenciales

### 2. Competencia
- Monitorea streamers competidores
- Analiza horarios de mayor actividad
- Identifica gaps de contenido

### 3. Networking
- Encuentra streamers para colaboraciones
- Identifica comunidades activas
- Construye listas de contactos

## 📈 Próximas Funcionalidades

- [ ] Export a CSV/JSON
- [ ] Integración con Discord/Telegram
- [ ] Análisis de tendencias
- [ ] Sistema de alertas
- [ ] Histórico de actividad

---

¿Tienes preguntas? Revisa el [README.md](README.md) principal o los logs en `tiktok_monitor.log`.
