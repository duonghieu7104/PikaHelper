@echo off
REM Script to copy Vietnamese embedding model to container (Windows)

echo Copying Vietnamese embedding model to container...

REM Check if model directory exists
if not exist "models\embedding" (
    echo Error: models\embedding directory not found!
    echo Please ensure you have the Vietnamese embedding model in models\embedding\
    pause
    exit /b 1
)

REM Create models directory in container if it doesn't exist
docker exec pika_embedding_service mkdir -p /app/models/embedding 2>nul

REM Copy model files to container
echo Copying model files...
docker cp models\embedding\. pika_embedding_service:/app/models/embedding/

echo Model copied successfully!
echo You can now restart the embedding service:
echo docker-compose restart embedding-service
pause
