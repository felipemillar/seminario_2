Manual de Operacionalización en Producción: Infraestructura de Trading Automatizado con TradingView

Arquitecturas de Referencia Operacionales

La transición de un modelo conceptual de trading algorítmico a un entorno de producción real exige una infraestructura diseñada bajo principios de alta disponibilidad, tolerancia a fallos y latencia determinista^1^. Dependiendo del capital gestionado, el volumen transaccional y los requisitos de cumplimiento normativo, se definen tres arquitecturas de referencia para la operacionalización de la ingesta de señales de TradingView y su posterior ejecución en brokers regulados^1^.

VPS Dedicado (Arquitectura Monolítica Optimizada)

Esta arquitectura concentra todos los componentes lógicos en una máquina virtual de alto rendimiento (vCPU optimizada para computación y almacenamiento de estado sólido NVMe) ubicada en un centro de datos co-localizado o con proximidad de red inmediata a los servidores de coincidencia (matching engines) del broker^1^.

El flujo se inicia cuando el proxy inverso Nginx intercepta la solicitud HTTPS entrante desde los servidores de TradingView, realiza la terminación SSL y valida el certificado del cliente a través de un socket Unix hacia el servidor de aplicaciones FastAPI^4^. FastAPI procesa la señal, delega el registro transaccional a una base de datos PostgreSQL local y despacha la orden de manera síncrona o asíncrona hacia las APIs del broker^6^.

[ TRADINGVIEW ] ──( HTTPS POST )──> [ NGINX Reverse Proxy ] ──( Unix Socket )──> [ FastAPI ] ──> [ PostgreSQL ]

                                                                                                   │

                                                                                                   └──> [ Broker API ]

Para asegurar la reproducibilidad de este entorno, se expone a continuación el archivo de configuración de orquestación de contenedores en producción (docker-compose.yml):

YAML

*version:* *'3.8'*

*services:*

  *nginx:*

    *image:* *nginx:1.25-alpine*

    *container_name:* *trading_nginx*

    *ports:*

      *-* *"80:80"*

      *-* *"443:443"*

    *volumes:*

      *-* *./nginx/conf.d:/etc/nginx/conf.d:ro*

      *-* *./nginx/certs:/etc/letsencrypt:ro*

      *-* */var/log/nginx:/var/log/nginx*

    *depends_on:*

      *-* *fastapi_app*

    *restart:* *always*

    *networks:*

      *-* *trading_network*

  *fastapi_app:*

    *build:*

      *context:* *.*

      *dockerfile:* *Dockerfile*

    *container_name:* *trading_fastapi*

    *environment:*

      *-* *DATABASE_URL=postgresql://trading_user:SecurePass2026@timescaledb:5432/trading_db*

      *-* *ENVIRONMENT=production*

    *volumes:*

      *-* */var/log/fastapi-app:/var/log/fastapi-app*

    *restart:* *always*

    *networks:*

      *-* *trading_network*

    *depends_on:*

      *-* *timescaledb*

  *timescaledb:*

    *image:* *timescale/timescaledb:latest-pg15*

    *container_name:* *trading_timescaledb*

    *environment:*

      *-* *POSTGRES_DB=trading_db*

      *-* *POSTGRES_USER=trading_user*

      *-* *POSTGRES_PASSWORD=SecurePass2026*

    *volumes:*

      *-* *timescaledb_data:/var/lib/postgresql/data*

    *ports:*

      *-* *"5432:5432"*

    *restart:* *always*

    *networks:*

      *-* *trading_network*

*volumes:*

  *timescaledb_data:*

*networks:*

  *trading_network:*

    *driver:* *bridge*

Serverless (Arquitectura de Escalabilidad Elástica)

Orientada a estrategias de baja a mediana frecuencia que buscan minimizar los costes fijos de mantenimiento de servidores encendidos continuamente^8^. AWS API Gateway actúa como el punto de enlace expuesto de manera pública, gestionando la capa de autorización e inyectando las peticiones a una función AWS Lambda dedicada.

La función Lambda se encarga de analizar el mensaje de la alerta, validar las claves de autenticación, interactuar con una base de datos NoSQL distribuida (Amazon DynamoDB) para el control de estados e idempotencia, y despachar la orden a la API del broker. Si bien elimina la administración de sistemas operativos, introduce una variabilidad de latencia crítica debido al arranque en frío (cold start) de las funciones Lambda.

[ TRADINGVIEW ] ──> [ AWS API Gateway ] ──> [ AWS Lambda ] ──> [ Amazon DynamoDB ]

                                                                     │

                                                                     └──> [ Broker API ]

Containerizada (Arquitectura Cloud-Native Altamente Disponible)

Pensada para operaciones de trading institucional, multi-cuenta y multi-broker con alta frecuencia de señales^3^. Se despliega un clúster de Kubernetes ligero (K3s) sobre un conjunto de nodos distribuidos en múltiples zonas de disponibilidad. Un controlador de Ingress (como Traefik) encamina las peticiones externas hacia un conjunto replicado de pods del webhook receiver de FastAPI.

Las señales no se envían directamente al broker; en su lugar, se inyectan en un sistema de mensajería altamente disponible (RabbitMQ) que gestiona la persistencia y distribución. Un conjunto independiente de pods ejecutores (Workers) consume las señales de la cola, calcula el tamaño de posición por cuenta y despacha las transacciones concurrentemente a los brokers, registrando la auditoría en un clúster distribuido de TimescaleDB^3^.

[ TRADINGVIEW ] ──> [ Traefik Ingress ] ──> [ FastAPI Pods ] ──> [ RabbitMQ ] ──> [ Executor Workers ] ──> [ TimescaleDB ]

                                                                                         │

                                                                                         └──> [ Broker APIs ]

Tabla Comparativa de Arquitecturas de Producción

La evaluación de la arquitectura óptima requiere analizar el equilibrio entre latencia, coste y tolerancia a fallos^1^:

| **Métrica de Comparación** | **VPS Dedicado** | **Serverless (AWS)** | **Containerizada (K3s)** |
| --- | --- | --- | --- |
| **Costo Mensual Base** | Bajo ($10.00 - $40.00 USD)^6^ | Variable (Escala por uso) | Alto ($150.00 - $400.00 USD) |
| **Complejidad DevOps** | Baja-Media^1^ | Media | Muy Alta |
| **Latencia Interna (P95)** |  |  |  |
| **Tolerancia a Fallos** | Único punto de fallo (Single node) | Excelente (Soporte Multi-AZ nativo) | Máxima (Auto-recuperación de pods) |
| **Esfuerzo de Mantenimiento** | Bajo^1^ | Mínimo | Alto (Mantenimiento de clúster) |
| **Límite de Concurrencia** | Acotado por CPU/RAM local | Prácticamente ilimitado | Alto (Escalado horizontal dinámico) |

SSL/TLS y Seguridad de Red de Nivel Industrial

La exposición de un endpoint público encargado de ejecutar órdenes financieras reales requiere la implementación de medidas de seguridad perimetral rigurosas para mitigar el riesgo de inyecciones de código, suplantación de identidad y ataques distribuidos de denegación de servicio (DDoS)^1^.

Obtención de Certificados SSL/TLS con Let's Encrypt

Para habilitar comunicaciones cifradas mediante HTTPS en el puerto estándar 443^8^, se utiliza la autoridad de certificación Let's Encrypt junto con el cliente Certbot^12^. La instalación y automatización de la renovación se efectúa mediante los siguientes comandos:

Bash

*# Actualizar el repositorio de paquetes e instalar Certbot con el plugin de Nginx*

sudo apt update

sudo apt install certbot python3-certbot-nginx -y

*# Solicitar el certificado SSL para el dominio de producción*

sudo certbot --nginx -d api.tradingbotproduccion.com --non-interactive --agree-tos --email ops@tradingbotproduccion.com

*# Verificar el temporizador de renovación automática del sistema systemd*

sudo systemctl status certbot.timer

Configuración del Proxy Inverso Nginx para Mutua Autenticación (mTLS)

TradingView transmite un certificado SSL cliente único a la dirección URL de destino cuando se utiliza el protocolo HTTPS^13^. Este comportamiento permite implementar un control de seguridad avanzado en la configuración de Nginx, validando criptográficamente si la petición procede genuinamente de los servidores de TradingView (cuyo certificado posee el nombre común o CN webhook-server@tradingview.com) antes de permitir el acceso al backend de FastAPI^13^:

Nginx

*# Configuración del módulo de asignación de tasa de solicitudes por IP (Rate Limiting)*

*limit_req_zone* $binary_remote_addr zone=api_limit_zone:*10m* rate=3r/s;

*server* {

    *listen* *80*;

    *server_name* api.tradingbotproduccion.com;

    *return* *301* https://$host$request_uri;

}

*server* {

    *listen* *443* ssl http2;

    *server_name* api.tradingbotproduccion.com;

    *# Certificados del Servidor (Let's Encrypt)*

    *ssl_certificate* /etc/letsencrypt/live/api.tradingbotproduccion.com/fullchain.pem;

    *ssl_certificate_key* /etc/letsencrypt/live/api.tradingbotproduccion.com/privkey.pem;

    *# Parámetros TLS Seguros y de Alto Rendimiento*

    *ssl_protocols* TLSv1.*2* TLSv1.*3*;

    *ssl_prefer_server_ciphers* *on*;

    *ssl_ciphers* *'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305'*;

    *ssl_session_cache* shared:SSL:*10m*;

    *ssl_session_timeout* *1d*;

    *ssl_session_tickets* *off*;

    *# Cabeceras de Seguridad HTTP para Hardening*

    *add_header* X-Frame-Options *"DENY"* always;

    *add_header* X-Content-Type-Options *"nosniff"* always;

    *add_header* X-XSS-Protection *"1; mode=block"* always;

    *add_header* Strict-Transport-Security *"max-age=63072000; includeSubDomains; preload"* always;

    *# Configuración de Validación del Certificado Cliente de TradingView*

    *# Para habilitarlo, es necesario descargar la CA intermedia de TradingView y apuntar a ella*

    *ssl_client_certificate* /etc/nginx/certs/tradingview_ca.crt;

    *ssl_verify_client* optional; *# Se establece opcional para permitir health checks internos*

    *location* /webhook {

        *# Validación de Identidad del Emisor del Certificado Cliente de TradingView*

        *if* ($ssl_client_verify != SUCCESS) {

            *return* *403* *"Cerrado: Error de autenticación TLS Cliente."*;

        }

        *# Validar específicamente el Common Name (CN) para mitigar falsificaciones*

        *if* ($ssl_client_s_dn !*~ "CN=webhook-server@tradingview.com")* {

            *return* *403* *"Cerrado: Certificado cliente no autorizado."*;

        }

        *# Aplicación del límite de solicitudes con ráfagas controladas*

        *limit_req* zone=api_limit_zone burst=*5* nodelay;

        *limit_req_status* *429*;

        *# Configuración del Proxy Inverso*

        *proxy_pass* http://127.0.0.1:8000;

        *proxy_set_header* Host $host;

        *proxy_set_header* X-Real-IP $remote_addr;

        *proxy_set_header* X-Forwarded-For $proxy_add_x_forwarded_for;

        *proxy_set_header* X-Forwarded-Proto $scheme;

        *proxy_set_header* X-SSL-Client-Cert $ssl_client_escaped_cert;

        *# Timeouts estrictos para no superar la ventana de procesamiento de TradingView (< 3s)*

        *proxy_connect_timeout* *2s*;

        *proxy_read_timeout* *2s*;

        *proxy_send_timeout* *2s*;

    }

    *# Endpoint de verificación de salud expuesto sin mTLS para UptimeRobot*

    *location* /health {

        *proxy_pass* http://127.0.0.1:8000/health;

        *limit_req* zone=api_limit_zone burst=*2*;

    }

}

Reglas de Cortafuegos de Red (UFW) y Whitelisting de IP

El cortafuegos a nivel de sistema operativo (UFW) debe restringir el acceso a los puertos de administración (SSH) y limitar de forma estricta las peticiones al puerto 443 únicamente desde las direcciones IP oficiales de TradingView^10^:

- 52.89.214.238
[cite: 10, 11]
- 34.212.75.30
[cite: 10, 11]
- 54.218.53.128
[cite: 10, 11]
- 52.32.178.7
[cite: 10, 11]

Los comandos de configuración del cortafuegos para su aplicación en el servidor Ubuntu/Debian son:

Bash

*# Restablecer las políticas del cortafuegos a denegación total por defecto*

sudo ufw default deny incoming

sudo ufw default allow outgoing

*# Permitir SSH únicamente para el desarrollo o administración segura*

sudo ufw allow 22/tcp

*# Permitir HTTPS únicamente para el rango de IPs oficiales de TradingView*

sudo ufw allow from 52.89.214.238 to any port 443 proto tcp

sudo ufw allow from 34.212.75.30 to any port 443 proto tcp

sudo ufw allow from 54.218.53.128 to any port 443 proto tcp

sudo ufw allow from 52.32.178.7 to any port 443 proto tcp

*# Habilitar el cortafuegos*

sudo ufw *enable*

Capa de Persistencia y Base de Datos para el Registro Transaccional

La persistencia segura de las señales y su posterior traducción en órdenes de compra y venta constituye el pilar fundamental para la auditoría operativa y la evaluación del desempeño sistemático del bot de trading^7^.

SQLite vs. PostgreSQL vs. TimescaleDB

La selección del motor de almacenamiento determina la resiliencia del sistema bajo condiciones de alta concurrencia y volumen de datos^9^:

| **Criterio** | **SQLite** | **PostgreSQL** | **TimescaleDB** |
| --- | --- | --- | --- |
| **Tipo de Almacenamiento** | Archivo local embebido^16^ | Relacional estándar | Relacional optimizado para series de tiempo^9^ |
| **Concurrencia de Escritura** | Baja (Bloqueo a nivel de archivo entero) | Alta (Bloqueo por fila transaccional) | Máxima (Estructura de *Hypertables* particionadas)^9^ |
| **Escalabilidad de Volumen** | (Degradación severa) | Medio () | Alta ( gracias a compresión activa)^14^ |
| **Consultas de Series de Tiempo** | Manuales y lentas | Soportadas mediante índices B-Tree | Nativas mediante funciones de agregación temporal^9^ |
| **Casos de Uso en Trading** | Desarrollo local o prototipos básicos^7^ | Gestión de cuentas y configuraciones | Registro de señales, órdenes, ejecuciones y ticks^7^ |

Esquema de Base de Datos para TimescaleDB

Este esquema optimizado utiliza las ventajas de TimescaleDB para estructurar las tablas transaccionales del ciclo de vida de los trades: la recepción de señales (alerts_received), el envío de órdenes (orders_sent), y la confirmación de la ejecución por parte del broker (fills_confirmed)^7^:

SQL

*-- Habilitar extensión TimescaleDB en PostgreSQL*

*CREATE* EXTENSION IF *NOT* *EXISTS* timescaledb CASCADE;

*-- Tabla 1: Registro de Señales Recibidas desde TradingView*

*CREATE* *TABLE* alerts_received (

    alert_id UUID *DEFAULT* gen_random_uuid(),

    received_at TIMESTAMPTZ *NOT* *NULL* *DEFAULT* clock_timestamp(),

    strategy_name *VARCHAR*(*100*) *NOT* *NULL*,

    symbol *VARCHAR*(*30*) *NOT* *NULL*,

    action *VARCHAR*(*10*) *NOT* *NULL*, *-- 'BUY', 'SELL', 'CLOSE'*

    price *NUMERIC*(*20*, *10*) *NOT* *NULL*,

    idempotency_hash *VARCHAR*(*64*) *NOT* *NULL*,

    raw_payload JSONB *NOT* *NULL*,

    *PRIMARY* KEY (alert_id, received_at)

);

*-- Tabla 2: Registro de Órdenes Despachadas al Broker*

*CREATE* *TABLE* orders_sent (

    order_id UUID *DEFAULT* gen_random_uuid(),

    alert_id UUID *NOT* *NULL*,

    alert_received_at TIMESTAMPTZ *NOT* *NULL*,

    sent_at TIMESTAMPTZ *NOT* *NULL* *DEFAULT* clock_timestamp(),

    broker_name *VARCHAR*(*50*) *NOT* *NULL*,

    account_id *VARCHAR*(*100*) *NOT* *NULL*,

    symbol *VARCHAR*(*30*) *NOT* *NULL*,

    order_type *VARCHAR*(*20*) *NOT* *NULL*, *-- 'MARKET', 'LIMIT', 'STOP'*

    quantity *NUMERIC*(*20*, *10*) *NOT* *NULL*,

    price *NUMERIC*(*20*, *10*),

    status *VARCHAR*(*20*) *NOT* *NULL* *DEFAULT* *'PENDING'*, *-- 'PENDING', 'SUBMITTED', 'FAILED'*

    broker_order_ref *VARCHAR*(*100*),

    *PRIMARY* KEY (order_id, sent_at),

    *FOREIGN* KEY (alert_id, alert_received_at) *REFERENCES* alerts_received(alert_id, received_at) *ON* *DELETE* RESTRICT

);

*-- Tabla 3: Registro de Ejecución y Confirmación de Operaciones (Fills)*

*CREATE* *TABLE* fills_confirmed (

    fill_id UUID *DEFAULT* gen_random_uuid(),

    order_id UUID *NOT* *NULL*,

    order_sent_at TIMESTAMPTZ *NOT* *NULL*,

    confirmed_at TIMESTAMPTZ *NOT* *NULL* *DEFAULT* clock_timestamp(),

    broker_fill_id *VARCHAR*(*100*) *NOT* *NULL*,

    executed_quantity *NUMERIC*(*20*, *10*) *NOT* *NULL*,

    executed_price *NUMERIC*(*20*, *10*) *NOT* *NULL*,

    commission *NUMERIC*(*15*, *6*) *DEFAULT* *0.0*,

    slippage *NUMERIC*(*20*, *10*) *DEFAULT* *0.0*,

    *PRIMARY* KEY (fill_id, confirmed_at),

    *FOREIGN* KEY (order_id, order_sent_at) *REFERENCES* orders_sent(order_id, sent_at) *ON* *DELETE* RESTRICT

);

*-- Crear Hypertables particionadas automáticamente cada 7 días para optimizar escrituras*

*SELECT* create_hypertable(*'alerts_received'*, *'received_at'*, chunk_time_interval *=>* *INTERVAL* *'7 days'*);

*SELECT* create_hypertable(*'orders_sent'*, *'sent_at'*, chunk_time_interval *=>* *INTERVAL* *'7 days'*);

*SELECT* create_hypertable(*'fills_confirmed'*, *'confirmed_at'*, chunk_time_interval *=>* *INTERVAL* *'7 days'*);

*-- Índices Secundarios de Rendimiento para Búsquedas por Símbolo y Referencia del Broker*

*CREATE* INDEX idx_alerts_symbol *ON* alerts_received (symbol, received_at *DESC*);

*CREATE* INDEX idx_orders_broker_ref *ON* orders_sent (broker_order_ref, sent_at *DESC*);

*CREATE* INDEX idx_orders_status *ON* orders_sent (status, sent_at *DESC*);

Script de Backup Automatizado para PostgreSQL/TimescaleDB

El archivo /opt/fastapi-app/scripts/backup.sh gestiona de manera desatendida copias de seguridad de la base de datos de producción y rota los archivos locales tras transcurrir 14 días:

Bash

*#!/bin/bash*

*set* -euo pipefail

DB_NAME=*"trading_db"*

DB_USER=*"trading_user"*

BACKUP_DIR=*"/var/backups/trading_db"*

DATE=$(date +*"%Y%m%d_%H%M%S"*)

BACKUP_FILE=*"**${BACKUP_DIR}**/**${DB_NAME}**_prod_**${DATE}**.sql.gz"*

RETENTION_DAYS=14

*# Crear directorio de copia de seguridad con permisos restrictivos*

mkdir -p *"**$BACKUP_DIR**"*

chmod 700 *"**$BACKUP_DIR**"*

*# Exportar contraseña temporalmente de forma segura para pg_dump*

*export* PGPASSWORD=*"SecurePass2026"*

logger -t db_backup *"Iniciando copia de seguridad de TimescaleDB..."*

*# Realizar el volcado estructurado con compresión máxima*

pg_dump -h localhost -U *"**$DB_USER**"* -d *"**$DB_NAME**"* | gzip -9 > *"**$BACKUP_FILE**"*

logger -t db_backup *"Copia de seguridad completada con éxito:* *$BACKUP_FILE**"*

*# Eliminar respaldos obsoletos*

find *"**$BACKUP_DIR**"* -name *"**${DB_NAME}**_prod_*.sql.gz"* -*type* f -mtime +*"**$RETENTION_DAYS**"* -delete

logger -t db_backup *"Limpieza de respaldos completada."*

*unset* PGPASSWORD

Para activar este script, se programa un cronjob ejecutando crontab -e y agregando la siguiente línea, garantizando que el proceso ocurra todos los días a las 23:30 (hora del cierre del servidor de trading diario):

Fragmento de código

30 23 * * * /bin/bash /opt/fastapi-app/scripts/backup.sh >> /var/log/fastapi-app/backup_execution.log 2>&1

Observabilidad, Monitoreo y Sistema de Alertas

Un sistema de trading automatizado en producción exige un control analítico riguroso del estado del servidor, los tiempos de procesamiento y las posibles excepciones del software para evitar pérdidas catastróficas^18^.

Inicialización de Sentry en FastAPI

Para capturar errores en tiempo de ejecución (como fallos en la red del broker o problemas en el análisis sintáctico de datos), se inicializa Sentry en la aplicación FastAPI^20^:

Python

*import* sentry_sdk

*from* sentry_sdk.integrations.fastapi *import* FastApiIntegration

sentry_sdk.init(

    dsn=*"https://tu_token_sentry@sentry.io/proyecto_id"*,

    integrations=[FastApiIntegration()],

    traces_sample_rate=*0.1*, *# Limitar tasa de muestreo de trazas para reducir sobrecarga de latencia*

    environment=*"production"*,

    send_default_pii=*False*

)

Configuración del Logging Estructurado JSON en FastAPI

El logging estructurado facilita que herramientas automatizadas analicen el historial del sistema^21^. El siguiente script reemplaza los manejadores de eventos por defecto de FastAPI y Uvicorn por un serializador JSON de alto rendimiento^21^:

Python

*import* sys

*import* logging

*from* loguru *import* logger

*import* json

*class* *JSONFormatter:*

    *"""Formatter para serializar los registros en cadenas JSON válidas."""*

    *def* *__call__**(self, record):*

        log_payload = {

            *"timestamp"*: record[*"date"*].isoformat(),

            *"level"*: record[*"level"*].name,

            *"message"*: record[*"message"*],

            *"module"*: record[*"name"*],

            *"line"*: record[*"line"*],

            *"exception"*: *None*

        }

        *if* record[*"exception"*]:

            log_payload[*"exception"*] = {

                *"type"*: *str*(record[*"exception"*].*type*),

                *"value"*: *str*(record[*"exception"*].value),

                *"traceback"*: record[*"exception"*].traceback

            }

        *return* json.dumps(log_payload) + *"\n"*

*# Desactivar manejadores por defecto de Loguru y configurar salida estándar JSON*

logger.remove()

logger.add(sys.stdout, *format*=JSONFormatter(), level=*"INFO"*)

*# Redirigir la salida del logging integrado de Python hacia Loguru*

*class* *InterceptHandler(logging.Handler):*

    *def* *emit**(self, record):*

        *try*:

            level = logger.level(record.levelname).name

        *except* ValueError:

            level = record.levelno

        logger.opt(depth=*6*, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=*0*)

Configuración de Logrotate para la Aplicación

Para mitigar problemas de saturación de disco derivados del volumen de logs almacenados en /var/log/fastapi-app/app.log^6^, se crea la directiva de configuración /etc/logrotate.d/fastapi-app^6^:

Fragmento de código

/var/log/fastapi-app/*.log {

    daily

    rotate 14

    compress

    delaycompress

    missingok

    notifempty

    copytruncate

    create 0660 deploy www-data

}

Exposición de Métricas de Prometheus y Configuración de Scraping

Utilizando el paquete prometheus-fastapi-instrumentator, se instrumenta FastAPI expidiendo métricas que puedan ser recolectadas por Prometheus^20^.

Python

*from* fastapi *import* FastAPI

*from* prometheus_fastapi_instrumentator *import* Instrumentator

app = FastAPI()

*# Inicializar y exponer endpoint de métricas*

Instrumentator().instrument(app).expose(app, endpoint=*"/metrics"*)

El archivo de configuración /etc/prometheus/prometheus.yml define cómo el servidor Prometheus recopila estos datos en intervalos de 5 segundos para mantener una resolución analítica casi en tiempo real^20^:

YAML

*global:*

  *scrape_interval:* *5s*

  *evaluation_interval:* *5s*

*scrape_configs:*

  *-* *job_name:* *'fastapi_trading_app'*

    *metrics_path:* *'/metrics'*

    *static_configs:*

      *-* *targets:* [*'localhost:8000'*]

Archivo de Unidad systemd para el Control de Procesos de FastAPI

El control del demonio de FastAPI en producción se gestiona de manera óptima en sistemas Linux utilizando systemd^1^, configurando el archivo /etc/systemd/system/fastapi-trading.service:

Ini, TOML

*[Unit]*

*Description*=FastAPI Webhook Receiver de Trading en Produccion

*After*=network.target timescaledb.service

*[Service]*

*User*=deploy

*Group*=www-data

*WorkingDirectory*=/opt/fastapi-app

*VirtualEnv*=/opt/fastapi-app/venv

*ExecStart*=/opt/fastapi-app/venv/bin/gunicorn -w *4* -k uvicorn.workers.UvicornWorker -b *127.0*.*0.1*:*8000* app.main:app --access-logfile /var/log/fastapi-app/access.log --error-logfile /var/log/fastapi-app/error.log

*Restart*=always

*RestartSec*=*3*

*LimitNOFILE*=*65536*

*[Install]*

*WantedBy*=multi-user.target

Notificación Crítica de Telegram por Bot HTTP

Ante eventos del sistema de nivel crítico (fallos de conexión con la API del bróker o indisponibilidad de saldos), se despachan alertas directas al canal privado de Telegram del operador^7^:

Python

*import* httpx

*from* loguru *import* logger

*async* *def* *send_telegram_alert**(message:* *str**):*

    bot_token = *"9988221144:AAHHFggJJKKLL"*

    chat_id = *"-10022334455"*

    url = *f"https://api.telegram.org/bot{bot_token}/sendMessage"*

    payload = {

        *"chat_id"*: chat_id,

        *"text"*: *f"*NOTIFICACIÓN DE TRADING ACTIVO* \n\n{message}"*,

        *"parse_mode"*: *"Markdown"*

    }

    *async* *with* httpx.AsyncClient() *as* client:

        *try*:

            response = *await* client.post(url, json=payload, timeout=*5.0*)

            *if* response.status_code != *200*:

                logger.error(*f"Fallo enviando mensaje a Telegram: {response.text}"*)

        *except* Exception *as* e:

            logger.error(*f"Excepción en el cliente de Telegram: {**str**(e)}"*)

Configuración de Monitoreo Externo con UptimeRobot y Healthchecks.io

Para implementar un sistema de alertas proactivo, se configuran dos plataformas externas de monitoreo^20^:

- **UptimeRobot**: Se configura una tarea de monitoreo HTTP GET apuntando a https://api.tradingbotproduccion.com/health programada a intervalos de 60 segundos^6^. Si el backend de FastAPI no devuelve un estado HTTP 200 o si la resolución del certificado SSL de Let's Encrypt falla^25^, UptimeRobot enviará alertas instantáneas a través de Slack o correo electrónico^20^.
- **Healthchecks.io**: Para asegurar que los scripts en segundo plano (como el archivo de copias de seguridad de la base de datos) se ejecuten correctamente, se añade la siguiente línea de ejecución al script Bash de backup^6^:
Bash
curl -fsS --retry 3 https://hc-ping.com/tu-uuid-identificador > /dev/null
Si el cronjob falla y no envía el ping correspondiente en el horario establecido, Healthchecks.io notificará la incidencia de forma inmediata^6^.

Dashboard de Rendimiento Analítico

El control visual del rendimiento histórico, el P&L y el control de drawdown en tiempo real permite al equipo de trading identificar anomalías en el comportamiento de las estrategias automatizadas^26^.

Panel de Control Desarrollado en Streamlit

Este desarrollo de Streamlit se conecta a la base de datos de TimescaleDB, procesa los datos agregados e históricos utilizando operaciones vectorizadas de Pandas y dibuja la curva de equity y la fluctuación del drawdown^26^:

Python

*import* streamlit *as* st

*import* pandas *as* pd

*import* numpy *as* np

*import* psycopg2

*import* plotly.express *as* px

st.set_page_config(page_title=*"Dashboard de Rendimiento Algorítmico"*, layout=*"wide"*)

st.title(*"Métricas de Desempeño y Control de Ejecución"*)

*@st.cache_data(ttl=**30**)*

*def* *load_performance_data**():*

    conn = psycopg2.connect(

        host=*"localhost"*,

        database=*"trading_db"*,

        user=*"trading_user"*,

        password=*"SecurePass2026"*

    )

    query = *"""

        SELECT 

            f.confirmed_at as timestamp,

            f.executed_quantity * f.executed_price as trade_value,

            o.action,

            f.commission,

            f.slippage

        FROM fills_confirmed f

        JOIN orders_sent o ON f.order_id = o.order_id

        ORDER BY f.confirmed_at ASC;

    """*

    df = pd.read_sql_query(query, conn)

    conn.close()

    *return* df

*try*:

    df = load_performance_data()

    *if* df.empty:

        st.info(*"Aún no existen transacciones registradas."*)

    *else*:

        capital_inicial = *10000.00*

        *# Calcular el P&L neto por operación contemplando costos de fricción de red y comisiones*

        df[*'net_pnl'*] = df.apply(

            *lambda* r: (r[*'trade_value'*] *if* r[*'action'*] == *'SELL'* *else* -r[*'trade_value'*]) 

                      - r[*'commission'*] - r[*'slippage'*], axis=*1*

        )

        *# Calcular de forma vectorizada la curva de balance acumulativo*

        df[*'equity_curve'*] = capital_inicial + df[*'net_pnl'*].cumsum()

        *# Calcular la serie histórica del Drawdown*

        df[*'peak'*] = df[*'equity_curve'*].cummax()

        df[*'drawdown'*] = (df[*'equity_curve'*] - df[*'peak'*]) / df[*'peak'*]

        *# Métricas Agregadas*

        pnl_total = df[*'net_pnl'*].*sum*()

        max_dd = df[*'drawdown'*].*min*() * *100.0*

        win_rate = (df[*'net_pnl'*] > *0*).mean() * *100.0*

        col1, col2, col3 = st.columns(*3*)

        col1.metric(*"Capital Neto Acumulado"*, *f"${df['equity_curve'].iloc[-**1**]:,**.2**f}"*)

        col2.metric(*"P&L Neto Total"*, *f"${pnl_total:+,**.2**f}"*)

        col3.metric(*"Drawdown Máximo Histórico"*, *f"{max_dd:**.2**f}%"*)

        *# Dibujar Curva de Equity con Plotly*

        st.subheader(*"Evolución Histórica del Balance"*)

        fig_equity = px.line(df, x=*'timestamp'*, y=*'equity_curve'*, labels={*'equity_curve'*: *'Equity ($)'*})

        fig_equity.update_layout(template=*"plotly_dark"*)

        st.plotly_chart(fig_equity, use_container_width=*True*)

        *# Dibujar Drawdown*

        st.subheader(*"Gráfico de Pérdidas de Capital (Drawdown)"*)

        fig_dd = px.area(df, x=*'timestamp'*, y=*'drawdown'*, labels={*'drawdown'*: *'Drawdown'*})

        fig_dd.update_layout(template=*"plotly_dark"*)

        st.plotly_chart(fig_dd, use_container_width=*True*)

*except* Exception *as* e:

    st.error(*f"Error procesando el dashboard analítico: {**str**(e)}"*)

Visualizador HTML Estático de Bajos Recursos con Chart.js

Para arquitecturas donde no se desea mantener un servidor Python activo procesando vistas en tiempo real (ahorro de RAM en VPS de bajos recursos)^6^, se puede exportar un archivo JSON periódico de datos desde un cronjob y representarlo en un archivo HTML estático interactivo mediante la librería Chart.js^29^:

HTML

*<!DOCTYPE* ***html****>*

*<**html* *lang**=**"es"**>*

*<**head**>*

    *<**meta* *charset**=**"UTF-8"**>*

    *<**title**>*Curva de Equity Estática*</**title**>*

    *<**script* *src**=**"https://cdn.jsdelivr.net/npm/chart.js"**></**script**>*

    *<**style**>*

        *body* *{ background-color:* *#121212**; color:* *#fff**; font-family: sans-serif; padding:* *40px**; }*

        *.container* *{ width:* *90%**; margin: auto; background-color:* *#1e1e1e**; padding:* *20px**; border-radius:* *10px**; }

    </**style**>*

*</**head**>*

*<**body**>*

    *<**div* *class**=**"container"**>*

        *<**h2**>*Rendimiento de Cuenta de Producción*</**h2**>*

        *<**canvas* *id**=**"equity_chart"* *height**=**"150"**></**canvas**>*

    *</**div**>*

    *<**script**>*

        *const* *timestamps = [**"2026-07-01"**,* *"2026-07-02"**,* *"2026-07-03"**,* *"2026-07-04"**];*

        *const* *values = [**10000.0**,* *10250.0**,* *9900.0**,* *10450.0**];*

        *const* *ctx =* *document**.getElementById(**'equity_chart'**).getContext(**'2d'**);*

        *new* *Chart(ctx, {*

            *type**:* *'line'**,*

            *data**: {*

                *labels**: timestamps,*

                *datasets**: [{*

                    *label**:* *'Equity ($)'**,*

                    *data**: values,*

                    *borderColor**:* *'#00ffff'**,*

                    *tension**:* *0.1**,*

                    *fill**:* *false*

                *}]

            },*

            *options**: {*

                *responsive**:* *true**,*

                *scales**: {*

                    *x**: {* *grid**: {* *color**:* *'#2c2c2c'* *} },*

                    *y**: {* *grid**: {* *color**:* *'#2c2c2c'* *} }

                }

            }

        });

    </**script**>*

*</**body**>*

*</**html**>*

Tolerancia a Fallos, Redundancia y Recuperación ante Desastres

El entorno operativo del trading algorítmico se enfrenta constantemente a desconexiones, tiempos de inactividad de las APIs de corretaje y fallos lógicos^1^. El sistema debe estar preparado para gestionar de forma proactiva estas incidencias^1^.

TradingView exige que la respuesta HTTP a un webhook se complete en un intervalo estricto de menos de  (incluyendo el tiempo consumido por la resolución DNS del dominio)^8^. Si el servidor receptor tarda más en responder debido a la lentitud del broker o a cuellos de botella en la base de datos, TradingView cancelará la solicitud inmediatamente, considerándola fallida y descartando de forma permanente la señal de trading^8^.

Para mitigar este riesgo, la arquitectura desacopla por completo la recepción del webhook de su posterior procesamiento y ejecución^3^. Al recibir una señal, FastAPI únicamente realiza una validación básica de formato, delega de manera asíncrona la ejecución en segundo plano y retorna una respuesta HTTP 202 Accepted en menos de ^2^. El proceso de ejecución en segundo plano utiliza un sistema de reintentos con retraso exponencial y amortiguación de picos aleatorios (jitter) para reintentar la operación ante problemas transitorios de red con el broker^31^, además de un patrón de disyuntor (Circuit Breaker) para desactivar los envíos si los fallos persisten y evitar el colapso del sistema.

FastAPI asíncrono con Circuit Breaker, Exponential Backoff y Jitter

Este código asíncrono implementa la cola y desacoplamiento para procesar las señales de manera resiliente, mitigando el riesgo de exceder la ventana de tiempo límite de 3 segundos de TradingView^8^:

Python

*import* asyncio

*import* random

*import* time

*from* fastapi *import* FastAPI, BackgroundTasks, HTTPException, status

*from* pydantic *import* BaseModel

*from* loguru *import* logger

app = FastAPI()

*class* *TradeAlert(BaseModel):*

    strategy_name: *str*

    symbol: *str*

    action: *str*

    quantity: *float*

    expected_price: *float*

    time_fired: *str*

*class* *CircuitBreaker:*

    *"""Implementación de disyuntor para evitar llamadas a APIs caídas del broker."""*

    *def* *__init__**(self, fail_threshold:* *int* *=* *3**, cooldown:* *float* *=* *30.0**):*

        self.fail_threshold = fail_threshold

        self.cooldown = cooldown

        self.state = *"CLOSED"* *# "CLOSED", "OPEN", "HALF-OPEN"*

        self.failures = *0*

        self.last_failure_time = *0.0*

    *def* *record_success**(self):*

        self.failures = *0*

        self.state = *"CLOSED"*

    *def* *record_failure**(self):*

        self.failures += *1*

        self.last_failure_time = time.time()

        *if* self.failures >= self.fail_threshold:

            self.state = *"OPEN"*

            logger.critical(*f"Circuit Breaker abierto. Bloqueando ejecuciones por {self.cooldown}s"*)

    *def* *allow_request**(self) -> bool:*

        *if* self.state == *"OPEN"*:

            *if* time.time() - self.last_failure_time > self.cooldown:

                self.state = *"HALF-OPEN"*

                *return* *True*

            *return* *False*

        *return* *True*

broker_cb = CircuitBreaker()

*async* *def* *submit_order_to_broker_backoff**(alert: TradeAlert):*

    *"""

    Despachador de órdenes asíncrono con Exponential Backoff y Jitter.

    Intenta ejecutar la transacción protegiendo el flujo mediante el Circuit Breaker.

    """*

    *if* *not* broker_cb.allow_request():

        logger.error(*f"Fallo crítico: No se puede procesar la alerta {alert.strategy_name}. El Broker no responde."*)

        *return*

    base_delay = *1.0* *# Segundo base para el backoff*

    max_retries = *3*

    *for* attempt *in* *range*(max_retries + *1*):

        *try*:

            *# Simulación de la comunicación por red con la API del Broker*

            *await* _call_broker_api(alert)

            *# Si tiene éxito, restablece el contador de fallos del Circuit Breaker*

            broker_cb.record_success()

            logger.info(*f"Orden ejecutada con éxito en el intento {attempt}"*)

            *return*

        *except* Exception *as* e:

            logger.warning(*f"Error de red en intento {attempt}: {**str**(e)}"*)

            *if* attempt == max_retries:

                broker_cb.record_failure()

                logger.error(*"Se ha alcanzado el límite de intentos de red para esta señal."*)

                *return*

            *# Algoritmo de Exponential Backoff con Jitter aleatorio*

            delay = (base_delay * (*2* ** attempt)) + random.uniform(*0.1*, *0.5*)

            *await* asyncio.sleep(delay)

*async* *def* *_call_broker_api**(alert: TradeAlert):*

    *# Simular una llamada con un 20% de probabilidad de fallo de red*

    *await* asyncio.sleep(*0.1*)

    *if* random.random() < *0.2*:

        *raise* ConnectionError(*"Timeout o pérdida de socket temporal del Broker."*)

*@app.post(**"/webhook"**, status_code=status.HTTP_202_ACCEPTED)*

*async* *def* *handle_webhook**(alert: TradeAlert, background_tasks: BackgroundTasks):*

    *"""

    Recibe la alerta, valida y devuelve inmediatamente HTTP 202 en menos de 100ms.

    La ejecución transaccional pesada se delega a las tareas en segundo plano.

    """*

    *# Programar la ejecución en segundo plano para evitar que el webhook de TradingView agote el tiempo de espera*

    background_tasks.add_task(submit_order_to_broker_backoff, alert)

    *return* {*"status"*: *"ACCEPTED"*, *"message"*: *"Procesando orden en segundo plano."*}

Idempotencia de Señales por Firma Criptográfica Unicidad

TradingView no garantiza la entrega única absoluta y sus servidores pueden retransmitir la señal si experimentan demoras de red interna^8^. Para evitar ejecuciones duplicadas de la misma alerta en el mercado, se genera un Hash SHA-256 de idempotencia derivado de los campos inmutables de la señal: time_fired (enviado desde TradingView usando {{time}} o {{timenow}})^2^, strategy_name, symbol y action^3^.

Antes de procesar cualquier transacción en segundo plano, se inserta el Hash en la tabla alerts_received que cuenta con una restricción de clave única (UNIQUE constraint). Si la base de datos devuelve un fallo de violación de restricción, el proceso finaliza de inmediato, evitando la doble ejecución de la orden en la cuenta^8^.

Runbook de Recuperación Manual ante Emergencias (Disaster Recovery)

Ante una interrupción prolongada de los servicios, se debe ejecutar el siguiente protocolo paso a paso para restaurar la operatividad de la infraestructura:

[ PASO 1: ACTIVAR MODO MANTENIMIENTO ]

  └─ Modificar Nginx para retornar HTTP 503 Service Unavailable de manera inmediata.

[ PASO 2: CONCILIAR INVENTARIO ]

  └─ Comparar las posiciones abiertas en los terminales de los brokers contra las órdenes confirmadas.

[ PASO 3: BALANCEO MANUAL DE POSICIONES ]

  └─ Ejecutar transacciones manuales correctivas para neutralizar o ajustar la exposición de riesgo de mercado.

[ PASO 4: DEPURACIÓN Y CAMBIO DE ESTADO ]

  └─ Marcar alertas inactivas en la base de datos y reiniciar los demonios FastAPI.

[ PASO 5: RETORNO OPERATIVO Y LOG DE AUDITORÍA ]

  └─ Retirar la regla de mantenimiento de Nginx y redactar informe con la métrica de desviación de precios.

Motor Multi-Cuenta y Multi-Broker

Las estrategias en producción a menudo se despliegan de forma distribuida en varias cuentas independientes^3^. Para gestionarlas de forma segura, el motor de enrutamiento debe procesar las operaciones de cada cuenta en hilos de ejecución aislados, evitando que el fallo en una de ellas afecte al resto^3^.

[ TRADINGVIEW ALERT ]

                                  │

                                  ▼

                    [ MULTI-ACCOUNT ROUTER ]

                                  │

         ┌────────────────────────┼────────────────────────┐

         ▼                        ▼                        ▼

  [ Cuenta A - IBKR ]     [ Cuenta B - Binance ]     [ Cuenta C - Broker ]

  Mult: 1.0 (Directo)     Sizing: 2% Balance         Mult: 0.5 (Micro)

El siguiente bloque de código implementa el motor de enrutamiento asíncrono para distribuir las órdenes simultáneamente a múltiples brokers, calculando el tamaño de la posición por cuenta de manera independiente y controlando las excepciones de forma aislada^3^:

Python

*import* asyncio

*from* typing *import* Dict, List

*from* pydantic *import* BaseModel

*from* loguru *import* logger

*class* *RoutingConfig(BaseModel):*

    account_id: *str*

    broker: *str*

    multiplier: *float*

    allocation_mode: *str* *# "MULTIPLIER" o "RISK_BASED"*

    risk_percentage: *float* = *1.0*

*# Distribución de Cuentas por Estrategia*

STRATEGY_ROUTING_DIRECTORY: Dict[*str*, List[RoutingConfig]] = {

    *"GOLD_BREAKOUT_PROD"*: [

        RoutingConfig(account_id=*"ACC_IBKR_01"*, broker=*"IBKR"*, multiplier=*1.0*, allocation_mode=*"MULTIPLIER"*),

        RoutingConfig(account_id=*"ACC_BINANCE_02"*, broker=*"BINANCE"*, multiplier=*0.5*, allocation_mode=*"MULTIPLIER"*),

        RoutingConfig(account_id=*"ACC_BROKER_03"*, broker=*"Broker"*, multiplier=*1.0*, allocation_mode=*"RISK_BASED"*, risk_percentage=*1.5*)

    ]

}

*class* *MultiAccountExecutor:*

    *def* *__init__**(self, broker_clients_api: Dict):*

        self.broker_clients = broker_clients_api

    *async* *def* *dispatch_multi_account**(self, tv_payload:* *dict**):*

        strategy = tv_payload.get(*"strategy_name"*)

        symbol = tv_payload.get(*"symbol"*)

        base_qty = *float*(tv_payload.get(*"quantity"*, *1.0*))

        *if* strategy *not* *in* STRATEGY_ROUTING_DIRECTORY:

            logger.warning(*f"Sin ruta multi-cuenta activa para: {strategy}"*)

            *return*

        accounts_to_trade = STRATEGY_ROUTING_DIRECTORY[strategy]

        execution_tasks = []

        *# Construir llamadas asíncronas para su envío paralelo*

        *for* account *in* accounts_to_trade:

            execution_tasks.append(

                self._execute_single_account_order(account, symbol, base_qty, tv_payload)

            )

        *# Despachar todas las órdenes de forma concurrente, aislando excepciones mutuas*

        *# return_exceptions=True evita que un fallo en la Cuenta 1 interrumpa la Cuenta 2*

        execution_results = *await* asyncio.gather(*execution_tasks, return_exceptions=*True*)

        *for* idx, res *in* *enumerate*(execution_results):

            acc_info = accounts_to_trade[idx]

            *if* *isinstance*(res, Exception):

                logger.critical(*f"Excepcion crítica en Cuenta {acc_info.account_id}: {**str**(res)}"*)

            *else*:

                logger.info(*f"Éxito en Cuenta {acc_info.account_id}. Ticket ID: {res}"*)

    *async* *def* *_execute_single_account_order**(self, account: RoutingConfig, symbol:* *str**, base_qty:* *float**, tv_payload:* *dict**) -> str:*

        *# 1. Resolver el Sizing específico de cada cuenta*

        final_quantity = base_qty
    *def* *__init__**(self, broker_clients_api: Dict):*

        self.broker_clients = broker_clients_api

    *async* *def* *dispatch_multi_account**(self, tv_payload:* *dict**):*

        strategy = tv_payload.get(*"strategy_name"*)

        symbol = tv_payload.get(*"symbol"*)

        base_qty = *float*(tv_payload.get(*"quantity"*, *1.0*))

        *if* strategy *not* *in* STRATEGY_ROUTING_DIRECTORY:

            logger.warning(*f"Sin ruta multi-cuenta activa para: {strategy}"*)

            *return*

        accounts_to_trade = STRATEGY_ROUTING_DIRECTORY[strategy]

        execution_tasks = []

        *# Construir llamadas asíncronas para su envío paralelo*

        *for* account *in* accounts_to_trade:

            execution_tasks.append(

                self._execute_single_account_order(account, symbol, base_qty, tv_payload)

            )

        *# Despachar todas las órdenes de forma concurrente, aislando excepciones mutuas*

        *# return_exceptions=True evita que un fallo en la Cuenta 1 interrumpa la Cuenta 2*

        execution_results = *await* asyncio.gather(*execution_tasks, return_exceptions=*True*)

        *for* idx, res *in* *enumerate*(execution_results):

            acc_info = accounts_to_trade[idx]

            *if* *isinstance*(res, Exception):

                logger.critical(*f"Excepcion crítica en Cuenta {acc_info.account_id}: {**str**(res)}"*)

            *else*:

                logger.info(*f"Éxito en Cuenta {acc_info.account_id}. Ticket ID: {res}"*)

    *async* *def* *_execute_single_account_order**(self, account: RoutingConfig, symbol:* *str**, base_qty:* *float**, tv_payload:* *dict**) -> str:*

        *# 1. Resolver el Sizing específico de cada cuenta*

        final_quantity = base_qty

        *if* account.allocation_mode == *"MULTIPLIER"*:

            final_quantity = base_qty * account.multiplier

        *elif* account.allocation_mode == *"RISK_BASED"*:

            *# Obtener el saldo de la cuenta desde la API del Broker*

            client = self.broker_clients[account.broker]

            account_balance = *await* client.get_balance(account.account_id)

            *# Calcular en base al precio de entrada y stop loss recibido*

            stop_distance = *abs*(*float*(tv_payload[*"expected_price"*]) - *float*(tv_payload[*"stop_loss"*]))

            final_quantity = (account_balance * (account.risk_percentage / *100.0*)) / stop_distance

        *# 2. Despachar al Broker correspondiente*

        client = self.broker_clients[account.broker]

        order_response = *await* client.send_order(

            account_id=account.account_id,

            symbol=symbol,

            action=tv_payload[*"action"*],

            quantity=final_quantity

        )

        *return* order_response[*"broker_order_ref"*]

Integración Práctica con Gateway de Broker Externo

Los brokers institucionales requieren habitualmente interactuar a través de un gateway intermedio que exponga servicios locales^1^. Este módulo de FastAPI recibe la alerta simplificada de TradingView, realiza un mapeo del símbolo para acomodarlo a los nombres nativos del bróker externo, genera un payload JSON adaptado y realiza una llamada interna HTTP POST síncrona de alto rendimiento hacia el puerto del gateway local^1^:

Python

*import* httpx

*from* fastapi *import* APIRouter, HTTPException, status

*from* pydantic *import* BaseModel

*from* loguru *import* logger

router = APIRouter()

*# Dirección IP del Gateway Broker local configurada en el contexto conceptual (Parallels / Red Interna)*
BROKER_GATEWAY_ENDPOINT = *"http://api.broker.com/api/v1/order"*

*# Diccionario estricto para mapear diferencias entre la nomenclatura de TradingView y el Broker*

MARKET_SYMBOL_MAP = {

    *"BTCUSD"*: *"BTCUSD"*,
    *"EURUSD"*: *"EURUSD"*,
    *"GBPUSD"*: *"GBPUSD"*,
    *"US30"*: *"DJI"*
}

*class* *TradingViewAlertPayload(BaseModel):*

    *# 2. Convertir la acción de la alerta en comandos enteros para Broker (0: BUY, 1: SELL)*

    action_type = *0* *if* alert.action.upper() == *"BUY"* *else* *1*

    *# 3. Construir el payload específico que requiere el adaptador de Brokers*

    broker_payload = {

        *"symbol"*: mapped_symbol,

        *"action"*: action_type,

        *"volume"*: *float*(alert.quantity),

        *"type"*: *"ORDER_TYPE_MARKET"*,

        *"magic"*: alert.magic_number,

        *"comment"*: *f"TV Signal: {alert.strategy_name}"*,

        *"price"*: *0.0*,                  *# Ejecución a Mercado (Market execution)*

        *"type_time"*: *"ORDER_TIME_GTC"*, *# Orden válida hasta que sea cancelada de forma explícita*

        *"type_filling"*: *"ORDER_FILLING_IOC"* *# Immediate or Cancel para evitar esperas por liquidez*

    }

    *# 4. Enviar de manera síncrona al Gateway utilizando timeouts estrictos para mitigar latencia*

    *async* *with* httpx.AsyncClient() *as* client:

        *try*:

            logger.info(*f"Redirigiendo orden al Gateway del Broker ({mapped_symbol} | Vol: {alert.quantity})..."*)

            response = *await* client.post(

                BROKER_GATEWAY_ENDPOINT,

                json=broker_payload,

                timeout=*2.0* *# Límite de procesamiento estricto (< 3 segundos de TradingView)*

            )

            *if* response.status_code == *200*:

                result = response.json()

                logger.info(*f"Éxito: Orden procesada en Broker. Ticket: {result.get('ticket')}"*)

                *return* {*"status"*: *"SUCCESS"*, *"broker_ticket"*: result.get(*"ticket"*)}

            *else*:

                logger.error(*f"Fallo en Gateway: El adaptador Broker retornó código {response.status_code}"*)

                *raise* HTTPException(

                    status_code=status.HTTP_502_BAD_GATEWAY,

                    detail=*"El Gateway del Broker remoto reportó un error al procesar el ticket."*

                )

        *except* httpx.RequestError *as* exc:

            logger.exception(*f"Excepción de conexión de red contra el Gateway de Broker: {**str**(exc)}"*)

            *raise* HTTPException(

                status_code=status.HTTP_504_GATEWAY_TIMEOUT,

                detail=*"No se pudo establecer comunicación con el Gateway local de Broker."*

            )

TCO (Total Cost of Ownership) y Costos Operativos

El coste total de propiedad (TCO) incluye la infraestructura, las licencias del proveedor de gráficos y los costes derivados del deslizamiento de precios (slippage) por la latencia de ejecución^2^.

┌─────────────────────────────────────────────────────────────┐

│              DESGLOSE MENSUAL DE COSTOS (TCO)               │

├─────────────────────────────────────────────────────────────┤

│ Perfil Profesional (~$200/mo)                               │

│  ██████████████████████████████████████████████████ (74%)   │

│  Suscripción TV: $56.49  | VPS: $120.00 | Grafana: $45.00   │

│                                                             │

│ Perfil Semi-Pro (~$80/mo)                                   │

│  ████████████████████ (37%)                                 │

│  Suscripción TV: $28.29  | VPS: $15.00  | Sentry: $9.00     │

│                                                             │

│ Perfil Hobbyist (~$30/mo)                                   │

│  ████████ (14%)                                             │

│  Suscripción TV: $12.95  | VPS: $5.00   | Monitoreo: $0.00  │

└─────────────────────────────────────────────────────────────┘

El desglose mensual detallado de costes por perfil de volumen operativo se describe a continuación^8^:

| **Concepto de Costo Mensual** | **Perfil Hobbyist ($30.00 USD/mo Base)** | **Perfil Semi-Pro ($80.00 USD/mo Base)** | **Perfil Profesional ($200.00 USD/mo Base)** |
| --- | --- | --- | --- |
| **Suscripción TradingView** | $12.95 USD (Plan Essential)^8^ | $28.29 USD (Plan Plus)^8^ | $56.49 USD (Plan Premium)^8^ |
| **Infraestructura Cloud** | $5.00 USD (DigitalOcean/Vultr 1vCPU, 1GB) | $15.00 USD (DigitalOcean 2vCPU, 4GB RAM) | $120.00 USD (Servidores Distribuidos AWS Multi-AZ) |
| **Monitoreo e Informes** | $0.00 USD (Healthchecks.io/UptimeRobot Free) | $9.00 USD (Sentry Plan Developer) | $45.00 USD (Grafana Enterprise + Loki Logs Cloud) |
| **Slippage Estimado (Fricción)** | Mínimo ($5.00 USD/operaciones bajas) | Medio ($30.00 USD/operaciones moderadas) | Alto ($250.00 - $500.00 USD/volumen grande) |
| **Costos Totales Promedio** | **~$17.95 USD/mes** | **~$82.29 USD/mes** | **~$471.49 USD/mes** |

Logging Avanzado y Análisis Post-Trade (Slippage)

El deslizamiento (slippage) es la diferencia económica entre el precio teórico en el que TradingView generó la alerta y el precio real ejecutado y confirmado por el liquidador del broker^2^. Para medir la eficiencia de la infraestructura, se debe registrar y analizar minuciosamente cada milisegundo de retardo en la transmisión de datos^2^:

Esta latencia total se compone de la suma de retardos de cada una de las capas de transporte involucradas^2^:

Formato de Registro de Auditoría de Alta Precisión

El log de auditoría se almacena en el TimescaleDB estructurado de la siguiente forma, permitiendo analizar de manera forense el pipeline operativo de la transacción^7^:

JSON

{

  *"order_uuid"*: *"e305e548-36c5-4a25-bc32-1cb4659f81f1"*,

  *"strategy_name"*: *"GOLD_BREAKOUT_PROD"*,

  *"symbol"*: *"XAUUSD"*,

  *"action"*: *"BUY"*,

  *"volume"*: *1.5*,

  *"timestamps"*: {

    *"tv_alert_fired_at"*: *"2026-07-15T10:00:00.105234Z"*,

    *"webhook_received_at"*: *"2026-07-15T10:00:00.312154Z"*,

    *"order_sent_at"*: *"2026-07-15T10:00:00.325987Z"*,

    *"fill_confirmed_at"*: *"2026-07-15T10:00:00.585412Z"*

  },

  *"latencies"*: {

    *"ingress_network_delay_ms"*: *206.92*,

    *"internal_fastapi_delay_ms"*: *13.83*,

    *"broker_execution_delay_ms"*: *259.425*,

    *"end_to_end_delay_ms"*: *480.178*

  },

  *"execution_metrics"*: {

    *"tv_expected_price"*: *2350.50*,

    *"broker_executed_price"*: *2350.62*,

    *"slippage_nominal"*: *-0.12*,

    *"slippage_percentage"*: *-0.0051*,

    *"commission_cost"*: *-2.50*

  }

}

Script de Procesamiento Post-Trade y Reportes Automatizados

Este programa en Python se ejecuta de forma automática en el servidor todos los viernes tras el cierre de operaciones. Su función es extraer los últimos 7 días de datos, procesar las estadísticas generales del comportamiento de la infraestructura y compilar un informe sobre la latencia de red y el deslizamiento de precios en el broker^2^:

Python

*import* pandas *as* pd

*import* numpy *as* np

*import* psycopg2

*from* tabulate *import* tabulate

*from* loguru *import* logger

*def* *query_weekly_execution_data**() -> pd.DataFrame:*

    conn = psycopg2.connect(

        host=*"localhost"*,

        database=*"trading_db"*,

        user=*"trading_user"*,

        password=*"SecurePass2026"*

    )

    *# Consulta SQL para calcular tiempos de procesamiento y diferencias de precios*

    query = *"""

        SELECT 

            a.received_at as alert_time,

            a.price as expected_price,

            o.sent_at as order_time,

            f.confirmed_at as fill_time,

            f.executed_price,

            o.action,

            o.quantity

        FROM fills_confirmed f

        JOIN orders_sent o ON f.order_id = o.order_id

        JOIN alerts_received a ON o.alert_id = a.alert_id

        WHERE f.confirmed_at >= clock_timestamp() - INTERVAL '7 days';

    """*

    df = pd.read_sql_query(query, conn)

    conn.close()

    *return* df

*def* *generate_post_trade_report**():*

    logger.info(*"Extrayendo histórico semanal de ejecuciones..."*)

    *try*:

        df = query_weekly_execution_data()

        *if* df.empty:

            logger.warning(*"No se encontraron registros en el rango de fechas especificado."*)

            *return*

        *# 1. Análisis de los tiempos del pipeline de ejecución (Milisegundos)*

        df[*'latency_ingress_ms'*] = (df[*'order_time'*] - df[*'alert_time'*]).dt.total_seconds() * *1000.0*

        df[*'latency_broker_ms'*] = (df[*'fill_time'*] - df[*'order_time'*]).dt.total_seconds() * *1000.0*

        df[*'latency_total_ms'*] = (df[*'fill_time'*] - df[*'alert_time'*]).dt.total_seconds() * *1000.0*

        *# 2. Análisis del Deslizamiento Financiero (Slippage)*

        *# Slippage = expected_price - executed_price (en órdenes de compra, menor precio es mejor)*

        df[*'slippage_value'*] = df.apply(

            *lambda* r: r[*'expected_price'*] - r[*'executed_price'*] *if* r[*'action'*].upper() == *"BUY"*

                      *else* r[*'executed_price'*] - r[*'expected_price'*], axis=*1*

        )

        df[*'slippage_loss_usd'*] = df[*'slippage_value'*] * df[*'quantity'*]

        *# 3. Consolidación de Resultados Estadísticos*

        analytics_table = [

            [*"Métrica de Latencia"*, *"Valor Promedio"*, *"Percentil 95 (P95)"*],

            [*"Retardo de Ingreso de Señal"*, *f"{df['latency_ingress_ms'].mean():**.2**f} ms"*, *f"{df['latency_ingress_ms'].quantile(**0.95**):**.2**f} ms"*],

            [*"Retardo de Ejecución Broker"*, *f"{df['latency_broker_ms'].mean():**.2**f} ms"*, *f"{df['latency_broker_ms'].quantile(**0.95**):**.2**f} ms"*],

            [*"Tiempo Total Pipeline (E2E)"*, *f"{df['latency_total_ms'].mean():**.2**f} ms"*, *f"{df['latency_total_ms'].quantile(**0.95**):**.2**f} ms"*]

        ]

        *# Resumen Financiero de Pérdidas por Slippage*

        total_slippage_loss = df[df[*'slippage_loss_usd'*] < *0*][*'slippage_loss_usd'*].*sum*()

        total_operations = *len*(df)

        operations_with_slippage = (df[*'slippage_loss_usd'*] < *0*).*sum*()

        report_body = *f"""

=============================================================================

             REPORTE SEMANAL DE AUDITORÍA OPERATIVA (POST-TRADE)

=============================================================================

Intervalo: Últimos 7 Días de Mercado Operado

Operaciones Totales Procesadas: {total_operations}

Porcentaje de Operaciones con Deslizamiento en Contra: {(operations_with_slippage / total_operations ** *100.0**):**.2**f}%

Impacto Total del Slippage Financiero: ${**abs**(total_slippage_loss):,**.2**f} USD

--- ESTADÍSTICAS DEL PIPELINE DE LATENCIA DE RED ---

{tabulate(analytics_table, headers="firstrow", tablefmt="grid")}

Métricas de Desviación de Precios de Entrada:

* Máximo Deslizamiento en Contra en una Operación: ${df['slippage_loss_usd'].**min**():,**.2**f} USD

* Deslizamiento Promedio por Operación: ${df['slippage_loss_usd'].mean():,**.4**f} USD

=============================================================================

        """*

        print(report_body)

        *# Opcional: Se puede concatenar el envío directo de este reporte HTML/Texto a través de Telegram*

    *except* Exception *as* e:

        logger.exception(*f"Error procesando el reporte post-trade semanal: {**str**(e)}"*)

*if* __name__ == *"__main__"*:

    generate_post_trade_report()

Fuentes citadas

- TradingView with VPS: Webhook & Alert Automation, https://tradingfxvps.com/tradingview-with-vps-webhook-alert-automation/
- TradingView alert delay causes and solutions - ClearEdge Automation, https://clearedge.trading/post/tradingview-alert-delay-causes-solutions
- TradingView Webhook Format: Every Payload Field Explained, https://www.tv-hub.org/blog/webhook-anatomy/
- Rate Limiting with NGINX - NGINX Community Blog, https://blog.nginx.org/blog/rate-limiting-nginx
- Protecting Against Bot Attacks Using Nginx Rate Limits | by Irtiza Hafiz - Medium, https://irtizahafiz.medium.com/protecting-against-bot-attacks-using-nginx-rate-limits-12872fcbaafd
- FastAPI Deployment Guide | Production Setup on VPS - RamNode, https://ramnode.com/guides/fastapi
- amirphl/simple-trader: A Go-based trading system with modular strategies, risk management, and exchange integration. - GitHub, https://github.com/amirphl/simple-trader
- Automating TradingView Alerts with a VPS and Webhooks: Architecture, Security, and Broker Integration Guide, https://www.vpsforextrader.com/blog/what-is-tradingview-and-how-to-use-it/
- How to Build a High-Performance Time-Series Database on OpenMetal, https://openmetal.io/resources/blog/how-to-build-a-high-performance-time-series-database-on-openmetal/
- Cómo configurar alertas webhook - TradingView, https://es.tradingview.com/support/solutions/43000529348/
- How to configure webhook alerts - TradingView, https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/
- Securing APIs with FastAPI - Stackademic, https://blog.stackademic.com/securing-apis-with-fastapi-489c3d4d1ea0
- Autenticación del webhook - TradingView, https://es.tradingview.com/support/solutions/43000680459/
- Time-Series Database: What It Is, How It Works, and When You Need One | Tiger Data, https://www.tigerdata.com/learn/time-series-database-what-it-is-how-it-works-and-when-you-need-one
- What Is a Time-Series Database? Examples, Use Cases & ClickHouse Guide | Engineering, https://clickhouse.com/resources/engineering/what-is-time-series-database
- Rate Limiting in FastAPI: What the Popular Libraries Miss - Reddit, https://www.reddit.com/r/FastAPI/comments/1s9nz1t/rate_limiting_in_fastapi_what_the_popular/
- The Best Time-Series Databases in 2026 (and How to Choose) - QuestDB, https://questdb.com/blog/best-time-series-databases/
- The Simplest Way to Make FastAPI Prometheus Work Like It Should - hoop.dev, https://hoop.dev/blog/the-simplest-way-to-make-fastapi-prometheus-work-like-it-should
- Prometheus on a FastAPI application | by Hitoruna - Medium, https://medium.com/@hitorunajp/prometheus-on-a-fastapi-application-aa25e5223a9e
- Monitoring FastAPI with Prometheus and Grafana - Medium, https://medium.com/@bhagyarana80/monitoring-fastapi-with-prometheus-and-grafana-2a1df999966f
- Bridging Python's Logging Module to OpenTelemetry (Complete Guide) - Dash0, https://www.dash0.com/guides/opentelemetry-logging-python
- Python Logging with Loguru: From Setup to Production - Dash0, https://www.dash0.com/guides/python-logging-with-loguru
- Log rotation results in lost or duplicate events | Beats - Elastic, https://www.elastic.co/docs/reference/beats/filebeat/file-log-rotation
- trallnag/prometheus-fastapi-instrumentator - GitHub, https://github.com/trallnag/prometheus-fastapi-instrumentator
- What do errors mean when sending webhooks - TradingView, https://www.tradingview.com/support/solutions/43000776894-what-do-errors-mean-when-sending-webhooks/
- How To Calculate The Drawdown In Python For Your Trading Strategy - QuantifiedStrategies.com, https://www.quantifiedstrategies.com/how-to-calculate-trading-drawdown-in-python/
- DEMO for INSPIRATION: investment portfolio chart dashboard - Show the Community!, https://discuss.streamlit.io/t/demo-for-inspiration-investment-portfolio-chart-dashboard/119602
- Live Stock Dashboard with Peer Analysis — Built with Streamlit (python), https://discuss.streamlit.io/t/live-stock-dashboard-with-peer-analysis-built-with-streamlit-python/120077
- Creating a Financial Dashboard Using Python and Streamlit | by Julian Marx - Medium, https://medium.com/data-science/creating-a-financial-dashboard-using-python-and-streamlit-cccf6c026676
- ClearEdge Automation, https://clearedge.trading/post/tradingview-webhook-failed-fix-alert-errors
- Python Monitoring with Prometheus (Beginner's Guide) | Better Stack Community, https://betterstack.com/community/guides/monitoring/prometheus-python-metrics/
- Webhook resubmission - TradingView, https://www.tradingview.com/support/solutions/43000735201-webhook-resubmission/
- TradingView Alerts Setup: Free Plan Limits (2026), https://www.tv-hub.org/guide/tradingview-alerts-setup