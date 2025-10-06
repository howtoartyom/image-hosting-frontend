#!/bin/bash

# Создаем директорию backups в текущей папке проекта
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql"

# Создаем директорию для бэкапов если её нет
mkdir -p "$BACKUP_DIR"

# Используем полное имя контейнера из docker compose
CONTAINER_NAME="image-hosting-frontend-db-1"

# Проверяем существование контейнера
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo "Error: Container $CONTAINER_NAME is not running"
    exit 1
fi

# Делаем бэкап с использованием полного имени контейнера
docker exec -t $CONTAINER_NAME pg_dump -U postgres images_db > "${BACKUP_DIR}/${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "Backup successfully created: ${BACKUP_DIR}/${BACKUP_FILE}"
    echo "Size: $(ls -lh ${BACKUP_DIR}/${BACKUP_FILE} | awk '{print $5}')"
else
    echo "Error creating backup"
    exit 1
fi
