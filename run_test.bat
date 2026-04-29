@REM @echo off
@REM chcp 65001 >nul

@REM echo ===================================================
@REM echo      INICIALIZANDO AMBIENTE DE TESTES DE CARGA
@REM echo ===================================================
@REM echo.

@REM echo [1/4] Derrubando containers antigos (Limpando a rede)...
@REM docker-compose down
@REM echo.

@REM echo [2/4] Ligando o Banco de Dados e o WordPress Principal...
@REM docker-compose up -d db wordpress1
@REM echo.

@REM echo [3/4] Pausa de 15 segundos para o MySQL estabilizar completamente...
@REM timeout /t 15 /nobreak
@REM echo.

@REM echo [4/4] Ligando o resto (Nginx, WP2, WP3 e Locust)...
@REM docker-compose up -d
@REM echo.

@REM echo ===================================================
@REM echo      AMBIENTE NO AR! SEU TESTE ESTA RODANDO.
@REM echo ===================================================
@REM echo.
@REM pause

@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

echo ===================================================
echo   AUTOMATIZADOR DE TESTES - GERACAO DE 36 GRAFICOS
echo ===================================================
echo AVISO: Este processo executara 36 testes de 3 minutos.
echo Tempo total estimado: 1 hora e 50 minutos.
echo Feche abas pesadas do navegador e deixe o PC trabalhar.
echo.
pause
echo.

:: 1. Limpeza inicial
echo [1/3] Limpando ambiente...
docker-compose down
        
:: 2. Sobe todos os WPs de uma vez
echo [2/3] Ligando a infraestrutura base...
docker-compose up -d wordpress3
echo Aguardando 20s para o MySQL e os WPs estabilizarem...
timeout /t 20 /nobreak

echo [3/3] Iniciando Bateria de Testes ^(36 Rodadas^)...

:: Loop 1: Quantidade de Instancias (1, 2, 3)
FOR %%I IN (1 2 3) DO (
    echo.
    echo ===============================================
    echo   MUDANDO ARQUITETURA PARA %%I INSTANCIA^(S^) WP
    echo ===============================================
            
    :: Recriar o nginx.conf dinamicamente
    echo events { worker_connections 1024; } > nginx.conf
    echo http { >> nginx.conf
    echo   upstream wordpress { >> nginx.conf
    echo       server wordpress1; >> nginx.conf
    if %%I GEQ 2 echo       server wordpress2; >> nginx.conf
    if %%I GEQ 3 echo       server wordpress3; >> nginx.conf
    echo   } >> nginx.conf
    echo   server { >> nginx.conf
    echo       listen 80 default_server; >> nginx.conf
    echo       listen [::]:80 default_server; >> nginx.conf
    echo       root /usr/share/nginx/html; >> nginx.conf
    echo       index index.php; >> nginx.conf
    echo       location / { >> nginx.conf
    echo           add_header X-Upstream $upstream_addr; >> nginx.conf
    echo           proxy_set_header Host $http_host; >> nginx.conf
    echo           proxy_set_header X-Real-IP $remote_addr; >> nginx.conf
    echo           proxy_set_header x-forwarded-for $proxy_add_x_forwarded_for; >> nginx.conf
    echo           proxy_pass http://wordpress; >> nginx.conf
    echo       } >> nginx.conf
    echo   } >> nginx.conf
    echo } >> nginx.conf

    :: Inicia ou Reinicia o Nginx
    docker-compose up -d nginx
    docker restart nginx_balancer
    timeout /t 5 /nobreak
            
    :: Loop 2: Qual Cenario rodar (1, 2, 3 ou TODOS)
    FOR %%C IN (1 2 3 TODOS) DO (
                
        :: Loop 3: Nivel de Carga (leve, medio, pesado)
        FOR %%L IN (leve medio pesado) DO (
                    
            :: Define o numero de usuarios e o hatch rate baseado no peso
            if "%%L"=="leve" ( set USERS=160 & set RATE=4 )
            if "%%L"=="medio" ( set USERS=240 & set RATE=10 )
            if "%%L"=="pesado" ( set USERS=360 & set RATE=13 )
                    
            echo.
            echo --- Testando: Cenario %%C ^| Carga %%L ^(!USERS! users^) ^| %%I WP^(s^) ---
                    
            :: Cria as pastas super organizadas
            if not exist "locust-scripts\resultados\%%I_instancias\cenario_%%C" mkdir "locust-scripts\resultados\%%I_instancias\cenario_%%C"
                    
            :: Executa o container do Locust (AGORA CORRIGIDO, SEM O DUPLO LOCUST)
            docker-compose run --rm -e CENARIO=%%C locust -f /mnt/locust/locustfile.py --host http://localhost:8080 --headless -u !USERS! -r !RATE! --run-time 3m --csv=/mnt/locust/resultados/%%I_instancias/cenario_%%C/resultado_%%L
        )
    )
)

echo.
echo ===================================================
echo TESTES FINALIZADOS COM SUCESSO!
echo Verifique a pasta "locust-scripts/resultados"
echo ===================================================
pause