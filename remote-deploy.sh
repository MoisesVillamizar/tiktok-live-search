#!/bin/bash

# KP DIGITAL - Remote Deployment Script
# Despliega automáticamente en servidor remoto via SSH

set -e

# Configuración del servidor
SERVER_USER="root"
SERVER_HOST="77.237.243.186"
DEPLOY_PATH="/root/tiktok-live-search"
FRONTEND_DOMAIN="kpdigital.aineo.space"
BACKEND_DOMAIN="kpbackend.aineo.space"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 KP DIGITAL - Deployment Automático${NC}"
echo -e "${YELLOW}Servidor: ${SERVER_HOST}${NC}"
echo ""

# Pedir password de forma segura
echo -n "Enter SSH password for ${SERVER_USER}@${SERVER_HOST}: "
read -s SERVER_PASSWORD
echo ""

# Función para ejecutar comandos via SSH
run_remote() {
    sshpass -p "${SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "$1"
}

# Verificar que sshpass está instalado
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}📥 Instalando sshpass...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    else
        sudo apt-get update && sudo apt-get install -y sshpass
    fi
fi

echo -e "${YELLOW}1️⃣  Instalando Docker en el servidor...${NC}"
run_remote "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && apt-get install -y docker-compose" || echo "Docker ya instalado"

echo -e "${YELLOW}2️⃣  Clonando/actualizando repositorio...${NC}"
run_remote "
if [ -d '${DEPLOY_PATH}' ]; then
    cd ${DEPLOY_PATH}
    git pull origin main
else
    git clone https://github.com/MoisesVillamizar/tiktok-live-search.git ${DEPLOY_PATH}
    cd ${DEPLOY_PATH}
fi
"

echo -e "${YELLOW}3️⃣  Configurando variables de entorno...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}Subiendo archivo .env local al servidor...${NC}"
    sshpass -p "${SERVER_PASSWORD}" scp -o StrictHostKeyChecking=no .env "${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/.env"
else
    echo -e "${YELLOW}⚠️  No se encontró .env local. Necesitas configurarlo en el servidor.${NC}"
    run_remote "cd ${DEPLOY_PATH} && cp .env.example .env"
    echo -e "${RED}❗ IMPORTANTE: Edita el archivo .env en el servidor con tus credenciales de TikAPI${NC}"
    echo -e "${YELLOW}Ejecuta: ssh ${SERVER_USER}@${SERVER_HOST} 'nano ${DEPLOY_PATH}/.env'${NC}"
fi

echo -e "${YELLOW}4️⃣  Desplegando con Docker Swarm Stack...${NC}"
run_remote "cd ${DEPLOY_PATH} && docker stack deploy -c docker-compose.yml kpdigital"

echo -e "${YELLOW}5️⃣  Esperando que el servicio inicie...${NC}"
sleep 15

echo -e "${YELLOW}6️⃣  Verificando estado del servicio...${NC}"
run_remote "docker service ls | grep kpdigital"

echo ""
echo -e "${GREEN}✅ ¡Deployment completado exitosamente!${NC}"
echo ""
echo -e "${GREEN}🌐 Tu aplicación está corriendo en:${NC}"
echo -e "${GREEN}   Frontend: https://${FRONTEND_DOMAIN}${NC}"
echo -e "${GREEN}   Backend:  https://${BACKEND_DOMAIN}${NC}"
echo -e "${GREEN}   IP:       http://${SERVER_HOST}:8000${NC}"
echo ""
echo -e "${YELLOW}📋 Comandos útiles:${NC}"
echo -e "   Ver logs:      ssh ${SERVER_USER}@${SERVER_HOST} 'docker service logs -f kpdigital_tiktok-monitor'"
echo -e "   Ver status:    ssh ${SERVER_USER}@${SERVER_HOST} 'docker service ps kpdigital_tiktok-monitor'"
echo -e "   Actualizar:    ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${DEPLOY_PATH} && docker stack deploy -c docker-compose.yml kpdigital'"
echo -e "   Detener:       ssh ${SERVER_USER}@${SERVER_HOST} 'docker stack rm kpdigital'"
echo ""
