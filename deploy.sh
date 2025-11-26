#!/bin/bash

# KP DIGITAL - TikTok Live Monitor Deployment Script
# Para Contabo/Hostinger u otros servidores VPS

set -e

echo "🚀 KP DIGITAL - Desplegando TikTok Live Monitor..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que exista .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: Archivo .env no encontrado${NC}"
    echo "Crea un archivo .env con tus credenciales de TikAPI"
    echo "Puedes usar .env.example como plantilla"
    exit 1
fi

# Crear directorio de datos si no existe
echo -e "${YELLOW}📁 Creando directorio de datos...${NC}"
mkdir -p data

# Detener contenedores existentes
echo -e "${YELLOW}🛑 Deteniendo contenedores existentes...${NC}"
docker-compose down || true

# Descargar última imagen de Docker Hub
echo -e "${YELLOW}📥 Descargando última imagen de Docker Hub...${NC}"
docker pull moivillaz/tiktok-live-search:latest

# Iniciar contenedores
echo -e "${YELLOW}▶️  Iniciando contenedores...${NC}"
docker-compose up -d

# Esperar a que el contenedor esté listo
echo -e "${YELLOW}⏳ Esperando que el servicio esté listo...${NC}"
sleep 10

# Verificar estado
echo -e "${YELLOW}🔍 Verificando estado del servicio...${NC}"
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Servicio desplegado exitosamente!${NC}"
    echo ""
    echo -e "${GREEN}🌐 La aplicación está corriendo en:${NC}"
    echo -e "${GREEN}   http://localhost:8000${NC}"
    echo ""
    echo -e "${YELLOW}📊 Ver logs:${NC} docker-compose logs -f"
    echo -e "${YELLOW}🛑 Detener:${NC} docker-compose down"
    echo -e "${YELLOW}🔄 Reiniciar:${NC} docker-compose restart"
else
    echo -e "${RED}❌ Error: El servicio no se inició correctamente${NC}"
    echo -e "${YELLOW}Ver logs:${NC} docker-compose logs"
    exit 1
fi
