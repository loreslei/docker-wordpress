@echo off
chcp 65001 >nul

echo ===================================================
echo      INICIALIZANDO AMBIENTE DE TESTES DE CARGA
echo ===================================================
echo.

echo [1/4] Derrubando containers antigos (Limpando a rede)...
docker-compose down
echo.

echo [2/4] Ligando o Banco de Dados e o WordPress Principal...
docker-compose up -d db wordpress1
echo.

echo [3/4] Pausa de 15 segundos para o MySQL estabilizar completamente...
timeout /t 15 /nobreak
echo.

echo [4/4] Ligando o resto (Nginx, WP2, WP3 e Locust)...
docker-compose up -d
echo.

echo ===================================================
echo      AMBIENTE NO AR! SEU TESTE ESTA RODANDO.
echo ===================================================
echo.
pause