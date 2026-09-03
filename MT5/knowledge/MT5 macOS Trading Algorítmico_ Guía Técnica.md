# **Arquitectura de Producción para Trading Algorítmico en MetaTrader 5 sobre macOS: Infraestructura, Automatización y Alta Disponibilidad**

El trading algorítmico profesional en mercados de divisas y derivados financieros exige un entorno de ejecución con una disponibilidad del 100% durante el horario de negociación (24/5), latencia de red ultra baja y tolerancia absoluta a fallos. Para un desarrollador que opera en hardware Apple Silicon (arquitecturas de procesador M1, M2, M3 o M4), ejecutar MetaTrader 5 (MT5) —una aplicación monolítica diseñada de forma nativa para las interfaces de programación de aplicaciones (API) Win32/Win64 de Windows— plantea desafíos arquitectónicos complejos.  
Este informe técnico analiza las alternativas de infraestructura, configuraciones óptimas de la plataforma, workflows de sincronización de código, esquemas de telemetría y planes de recuperación ante desastres requeridos para operar sistemas automáticos en producción de manera mantenible y altamente fiable.

## **1\. MetaTrader 5 para macOS Nativo y Capas de Compatibilidad**

La distribución oficial de MetaTrader 5 proporcionada por MetaQuotes para macOS no constituye un binario compilado de manera nativa para la arquitectura de hardware Apple Silicon ni para el sistema operativo macOS.1 En su lugar, el instalador empaqueta un prefijo autocontenido de la capa de compatibilidad Wine (frecuentemente utilizando el motor comercial de CrossOver).1

   
           │  
           ▼  
    (Traducción de APIs de Windows a APIs de macOS / POSIX)  
           │  
           ▼  
   (Traducción de instrucciones x86\_64 a ARM64)  
           │  
           ▼

### **Proceso de Instalación y Requerimientos del Sistema**

El instalador oficial para macOS se descarga como un archivo de imagen de disco (.dmg) firmado.1 Durante la instalación, que requiere como mínimo macOS Catalina (10.15.7) 1, el asistente de MetaQuotes inicializa de forma automática la botella de Wine, descargando e instalando los entornos de ejecución necesarios, tales como Mono (para la emulación de.NET) y Gecko.1 Alternativamente, se puede gestionar la compatibilidad mediante PlayOnMac, que facilita la creación de prefijos de Wine aislados para evitar conflictos entre diferentes compilaciones de terminales.1

### **Rendimiento bajo Emulación en Apple Silicon**

El rendimiento gráfico y de computación mononúcleo en procesadores M1/M2/M3/M4 es fluido para tareas analíticas discretas debido a la potencia intrínseca del hardware de Apple.1 Sin embargo, la pila de software de producción se enfrenta a una penalización de rendimiento de doble capa 2:

1. **Capa de traducción de API (Wine)**: Las llamadas al sistema de Windows (Win32/64) se interceptan y traducen a llamadas POSIX de macOS.1  
2. **Capa de traducción de instrucciones (Rosetta 2\)**: Al no existir un binario nativo ARM64 de MT5, macOS debe traducir dinámicamente el código binario compilado para x86\_64 a instrucciones ARM64.2

Esta traducción introduce micro-retrasos no deterministas en la ejecución de hilos, inaceptables para algoritmos que dependen de la precisión temporal en la recepción del flujo de datos de ticks.

### **Matriz de Funcionalidades Soportadas y Restricciones Técnicas**

La viabilidad de esta alternativa depende del nivel de acoplamiento del algoritmo con las API del sistema operativo Windows.2

| Subsistema de MT5 | Estado de Compatibilidad | Causa Raíz y Limitación Técnica |
| :---- | :---- | :---- |
| **Gráficos e Indicadores Visuales** | Soportado con inestabilidades 1 | El renderizado de objetos GDI funciona, pero el refresco rápido de ticks provoca parpadeos por la falta de traducción directa a Metal.5 |
| **EAs basados en MQL5 Puro** | Completamente Soportado 1 | Viable si la lógica operativa se limita al cálculo matemático estándar y llamadas internas de la API de MQL5. |
| **Importación de DLLs Externas** | **Inestable / No Soportado** 2 | Las librerías de enlace dinámico (.dll) compiladas para x86\_64 a menudo fallan al interactuar con el subsistema de memoria de Wine en ARM64.5 |
| **Aceleración OpenCL** | **No Soportado** 5 | Wine no traduce de forma nativa las llamadas de cómputo GPU de OpenCL o las APIs de DirectX 12 a la arquitectura de sombreadores de Apple Metal.7 |
| **Conectividad de Red Externa** | Soportado con restricciones | Las conexiones HTTPS mediante WebRequest funcionan, pero las integraciones mediante sockets directos o WebSockets a menudo sufren caídas. |

### **Acceso a la API de Python desde macOS Nativo**

La biblioteca oficial de integración de Python (MetaTrader5) no funciona en macOS nativo.8 Dicha librería depende de llamadas de comunicación entre procesos (IPC) a nivel de kernel de Windows que Wine no puede mapear.8  
Para solventar esta limitación y permitir el desarrollo algorítmico local en Python sobre macOS, se debe implementar una infraestructura de puente basada en contenedores de Docker 8:

Bash  
\# Inicialización de Colima forzando la emulación x86\_64 mediante QEMU sobre Apple Silicon  
colima start \--arch x86\_64 \--vm-type=qemu \--cpu 4 \--memory 8

En el contenedor Docker, se instala un entorno headless de Wine \+ Python para Windows, exponiendo un servidor de sockets TCP en el puerto 8001\.8 Desde el script de Python nativo en macOS, se realiza la comunicación mediante un cliente de abstracción puente como siliconmetatrader5 8:

Python  
from siliconmetatrader5 import MetaTrader5

\# Conexión al puente TCP/IP expuesto por el runtime de Docker  
mt5 \= MetaTrader5(host="localhost", port=8001, keepalive=True)

if not mt5.initialize():  
    print("Error al inicializar el puente de comunicación con MT5")  
    mt5.shutdown()

Esta solución es óptima para la fase de investigación, backtesting y desarrollo local en macOS, pero se descarta rigurosamente para la ejecución de trading algorítmico en vivo con capital real debido al overhead de latencia de red inducido por la emulación de QEMU.8

## **2\. Virtualización Local en Apple Silicon**

Para mantener el control físico de la ejecución en la oficina o centro de datos del operador, la virtualización de Windows 11 sobre ARM es la alternativa más común.2

### **Análisis de Hipervisores en Apple Silicon**

La virtualización sobre el silicio de Apple requiere hipervisores compatibles con el framework de virtualización nativo de macOS.4

* **Parallels Desktop**: Es la única solución comercial autorizada oficialmente por Microsoft para ejecutar Windows 11 ARM en Apple Silicon.10 Integra el motor de traducción de instrucciones **Prism**, el cual traduce de forma transparente el código compilado para x64 (como MT5) a ARM64 con un rendimiento cercano al nativo.10  
* **VMware Fusion Pro**: Ofrece una alternativa de virtualización robusta, pero la instalación de Windows 11 ARM requiere la descarga manual de la ISO y la inyección manual de controladores de red durante la fase OOBE (*Out-of-Box Experience*) mediante el comando OOBE\\BYPASSNRO en el terminal de Windows.  
* **UTM (QEMU)**: Hipervisor de código abierto enfocado en la emulación.8 Aunque permite ejecutar Windows ARM, carece de controladores de aceleración gráfica estables para Windows 11 y el rendimiento de la emulación de CPU x86\_64 pura en UTM es sumamente lento, inhabilitando su uso en trading algorítmico multiproceso.5

### **Configuración Óptima de Recursos en Parallels Desktop**

Para un funcionamiento continuo y estable de MetaTrader 5, se deben asignar recursos estáticos a la máquina virtual evitando la sobreasignación que comprometa al sistema host de macOS 4:

* **CPU**: Asignar un número par de núcleos físicos (mínimo 4).4 Se desaconseja asignar más del 50% de los núcleos de CPU disponibles en el SoC Apple Silicon para evitar el estrangulamiento térmico y la contención en los núcleos de eficiencia.  
* **RAM**: Asignar entre 6 GB y 8 GB de memoria RAM de forma estática.4 Esta asignación deja suficiente espacio de intercambio de sistema para el almacenamiento en caché de ticks históricos sin provocar swapping en el disco duro SSD de macOS.  
* **Almacenamiento**: Utilizar discos virtuales NVMe virtuales expandibles. Es crítico habilitar la opción de exclusión del archivo de la máquina virtual de las copias de seguridad automáticas de Apple Time Machine para evitar la congelación del disco durante ciclos intensivos de escritura de logs de MT5.

### **Estabilidad 24/5 y Resolución de Fallos Críticos**

Se han documentado fallos de inestabilidad graves en Windows 11 ARM bajo Parallels Desktop a partir de actualizaciones críticas del sistema operativo (como la KB5086672 o parches de seguridad de inicios de 2026).9 El síntoma reportado es una caída repentina de la máquina virtual con un error de tipo DRIVER\_POWER\_STATE\_FAILURE (9f) en el volcado de memoria de Windows (minidump).11 Este error es provocado por una falta de respuesta de los controladores del hipervisor de Parallels ante los cambios en el estado de energía de Windows.11  
Para estabilizar una máquina virtual que deba operar de forma continua 24/5, se deben aplicar las siguientes directivas de depuración en Parallels 9:

1. **Cambio de Hipervisor**: Apagar la VM, ir al Centro de Control de Parallels \-\> Configuración de la VM \-\> Pestaña Hardware \-\> CPU & Memoria \-\> Avanzado \-\> Cambiar el motor de hipervisor de "Parallels" a "Apple".9  
2. **Desactivar Optimización de Recursos**: Desmarcar la opción "Optimización automática de recursos" en Parallels.9 Esta opción suspende dinámicamente recursos de CPU del guest cuando detecta que no hay interacción del usuario a través de la interfaz RDP o local, deteniendo el hilo de ejecución de los EAs.  
3. **Pausar Actualizaciones de Windows**: Bloquear de forma explícita las actualizaciones automáticas de Windows 11 y desinstalar inmediatamente las KB que causen inestabilidad en los controladores de red virtualizados.9

### **Inviabilidad de las Soluciones de Virtualización Local en Producción**

A pesar del rendimiento de hardware que ofrecen los procesadores M1-M4, mantener un entorno de ejecución algorítmica local en macOS es inviable en entornos profesionales debido a los siguientes factores de riesgo estructurales 2:

* **Suspensión de Estado**: El cierre accidental de la tapa de un MacBook o el estado de reposo de ahorro de energía de un iMac suspende de inmediato la ejecución de la máquina virtual y los EAs activos, perdiendo la sincronización con el broker.2  
* **Vulnerabilidad de Suministro**: El suministro eléctrico y la red de banda ancha residenciales carecen de las garantías de redundancia física de un centro de datos corporativo, exponiendo al algoritmo a quedar desprotegido en momentos de alta volatilidad (slippage y pérdidas de stop-loss).2

## **3\. Servidores Privados Virtuales (VPS) Windows para MetaTrader 5**

Para el trading algorítmico profesional, la regla de diseño estándar es la co-ubicación física: situar el motor de ejecución en el mismo centro de datos que alberga el motor de emparejamiento (*matching engine*) del broker.2 Pepperstone, por ejemplo, sitúa sus servidores principales de ejecución de divisas en los centros de datos **Equinix LD4 (Londres)** y **Equinix NY4 (Secaucus, Nueva Jersey)**.13  
A continuación se detalla una evaluación analítica de los principales proveedores de infraestructura VPS del sector 12:

| Proveedor VPS | Plan Recomendado | Especificaciones de Hardware (VCPU / RAM / SSD) | Ubicaciones Clave de Co-ubicación | Latencia Media Pepperstone (LD4 / NY4) | Costo Mensual Promedio (2026) | SLA de Uptime Garantizado |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Beeks Financial Cloud** 22 | Bronze 16 | 1 vCPU Cores / 2.56 GB RAM / 30 GB SSD 16 | Equinix LD4, NY4, Hong Kong, Singapur 14 | ![][image1] (Enlace de fibra directa) 14 | £31.00 (![][image2]) 16 | 99.99% (Servicios redundados a nivel institucional) 14 |
| **ForexVPS.net** 14 | Core 15 | 2 vCPU Cores / 4 GB RAM / 100 GB SSD 15 | Equinix LD4, NY4, Fráncfort, Tokio, Singapur 23 | ![][image3] 12 | ![][image4] (Pago anual) 17 | 99.99% 17 |
| **TradingFX VPS** 18 | Advanced 18 | 2 Cores AMD Ryzen (4.3 GHz) / 4 GB DDR5 / 40 GB NVMe 18 | Equinix LD4, NY4, Aurora (Chicago CME) 26 | ![][image3] | ![][image5] (Pago anual) 18 | 99.99% 27 |
| **Contabo** 19 | Cloud VPS 20 19 | 6 vCPU AMD Cores / 12 GB RAM / 100 GB NVMe 19 | Reino Unido, Alemania, EE. UU., Singapur 19 | ![][image6] \- ![][image7] (Enrutamiento general corporativo) | ![][image2] 19 | 99.9% 28 |
| **AWS Lightsail** 20 | Medium Windows 20 | 2 vCPU Cores / 4 GB RAM / 80 GB SSD 20 | Global (13 regiones AWS) 29 | ![][image8] \- ![][image6] (Enrutamiento por red elástica general) | ![][image9] 20 | 99.99% 30 |
| **Vultr** 23 | Windows Cloud Compute | 2 vCPU Cores / 4 GB RAM / 80 GB NVMe | Global (32 ubicaciones) | ![][image10] \- ![][image11] | ![][image12] | 99.99% |
| **Google Cloud Platform** | Compute Engine n2-standard-2 | 2 vCPU Cores / 8 GB RAM / 100 GB SSD | Global | ![][image8] \- ![][image6] | ![][image2] (Instancia bajo demanda) | 99.99% |
| **Microsoft Azure** | B2s VM v2 | 2 vCPU Cores / 4 GB RAM / 64 GB SSD | Global | ![][image13] \- ![][image11] | ![][image2] | 99.99% |

### **Enrutamiento de Baja Latencia frente a Infraestructura en la Nube Generalista**

La diferencia sustancial entre los proveedores de VPS de trading especializados (Beeks, ForexVPS, TradingFX) y los gigantes de la nube pública (AWS, GCP, Azure) radica en la arquitectura de red 12:

1. **Pila de red de baja latencia y Jitter**: Los VPS especializados utilizan cross-connects directos de fibra óptica dentro de las mismas instalaciones de Equinix, garantizando un retardo constante y libre de variaciones abruptas (*jitter*).14 AWS y Azure dirigen sus paquetes a través de enrutadores WAN elásticos e interfaces virtuales que sufren de degradación de latencia temporal ante picos de congestión global.22  
2. **Costos Ocultos de Almacenamiento y Ancho de Banda**: En AWS Lightsail y las plataformas de nube tradicionales, la facturación del tráfico saliente (egress) es sumamente agresiva (![][image14] en AWS).30 Un EA de alta frecuencia que procese un flujo constante de cotizaciones tick a tick en múltiples pares puede generar cientos de gigabytes de logs de red, resultando en facturas de red imprevistas.30 Adicionalmente, los snapshots y copias de seguridad de volumen se cobran mensualmente por gigabyte ocupado (![][image15]).30

## **4\. Configuración Óptima de MetaTrader 5 en el VPS**

Para optimizar el rendimiento y evitar picos de uso del procesador que deriven en la congelación del sistema operativo, el terminal de MT5 debe despojarse de la carga gráfica y de procesamiento redundante.32

### **Configuración para la Reducción de Consumo de Recursos en MT5**

Por defecto, la instalación de MetaTrader 5 está orientada al análisis técnico manual. En un entorno de trading algorítmico desatendido, se deben aplicar las siguientes configuraciones de bajo consumo 32:

* **Reducción del Historial Visible**: En el menú Tools \-\> Options \-\> Charts, modificar el parámetro **"Max bars in history"** a ![][image16] (o el mínimo requerido por el EA para el cálculo de sus indicadores) y **"Max bars in chart"** a ![][image17].33 Mantener el valor por defecto de ![][image18] o superior obliga al terminal a retener megabytes de ticks en RAM de manera ineficiente.33  
* **Desactivar el Feed de Noticias**: Ir a Tools \-\> Options \-\> Server y desmarcar la opción **"Enable News"**.33 Esto corta la descarga y almacenamiento en caché de noticias financieras del broker que consumen hilos de CPU en segundo plano.33  
* **Limitar Símbolos en el Market Watch**: El Market Watch procesa ticks entrantes en tiempo real para todos los símbolos visibles, recalculando la matriz de spreads para cada uno.32 Se debe hacer clic derecho sobre la ventana de Market Watch, seleccionar **"Hide All"** 33, y posteriormente volver a añadir únicamente los activos financieros específicos sobre los cuales opera el EA.  
* **Deshabilitar Alertas Visuales e Indicadores Redundantes**: Eliminar todo indicador técnico de los gráficos abiertos (como nubes de Ichimoku o promedios pesados) que no sea estrictamente requerido por la lógica interna del EA.33 Los cálculos visuales consumen hilos críticos que deben estar reservados exclusivamente para la API de trading.  
* **Optimización de Audio y Alertas**: En Tools \-\> Options \-\> Events, desmarcar la casilla "Enable" para evitar que el terminal consuma memoria inicializando controladores de audio virtuales en segundo plano.

### **Automatización del Arranque de MT5 ante Reinicios de la VPS**

Para garantizar la continuidad operativa ante una actualización programada o un reinicio forzado del servidor físico del VPS 36:

1. **Configurar Windows Autologon**: Descargar la utilidad oficial de Microsoft Autologon.exe.37 Introducir las credenciales del Administrador de la VPS para almacenar la clave de manera encriptada en el registro de Windows.37 Esto permite saltarse la pantalla de login tras un reinicio del sistema.37  
2. **Acceso a la Carpeta de Inicio de Windows**: Abrir el cuadro de diálogo Ejecutar en Windows (Win \+ R), escribir shell:startup y presionar Enter para abrir el directorio de arranque del usuario.36  
3. **Creación del Acceso Directo de MT5**: Crear un acceso directo al binario de ejecución terminal64.exe (ubicado típicamente en C:\\Program Files\\MetaTrader 5\\) y pegarlo en esta carpeta.36

### **Configuración del EA para Carga y Ejecución Automática al Arranque**

Para asegurar que el EA se adjunte al gráfico con sus respectivos parámetros y comience a negociar de forma autónoma:

1. **Configurar el Perfil**: Adjuntar el EA en los gráficos necesarios, cargando los archivos de parámetros correspondientes (.set). Guardar el perfil con el nombre de Default en File \-\> Profiles \-\> Save As.  
2. **Parámetros de Línea de Comandos**: Configurar el acceso directo de MT5 creado en la carpeta de inicio de Windows modificando su campo "Target" o "Destino" de la siguiente manera:  
   DOS  
   "C:\\Program Files\\MetaTrader 5\\terminal64.exe" /profile:Default /login:XXXXX

3. **Validación Global de Autotrading**: Asegurar que la casilla **"Allow Algo Trading"** esté marcada globalmente en Tools \-\> Options \-\> Expert Advisors para evitar que el terminal bloquee la ejecución del EA en el arranque del servicio.

### **Optimización del Sistema Operativo Windows Server para Trading**

Para garantizar la prioridad de ejecución y evitar interrupciones de mantenimiento del procesador 32:

* **Configuración del Plan de Energía**: En el Panel de Control, cambiar la configuración a **"High Performance"** (Alto Rendimiento).32 En los ajustes avanzados del procesador, forzar tanto el estado mínimo como el máximo del procesador al ![][image19].32  
* **Programación de Tareas de CPU**: En System Properties \-\> Advanced \-\> Performance Settings \-\> Advanced, cambiar la asignación de recursos a **"Background services"**.32 Esto da prioridad de procesamiento a los subprocesos de los EAs por encima del renderizado gráfico interactivo del sistema.32  
* **Inhabilitar Updates Automáticos Intrusivos**: Mediante el editor de políticas de grupo (gpedit.msc), navegar a Computer Configuration \-\> Administrative Templates \-\> Windows Components \-\> Windows Update y deshabilitar las actualizaciones automáticas durante horas de mercado.  
* **Exclusiones en el Antivirus**: Configurar Windows Defender para omitir el escaneo de archivos en tiempo real en la carpeta de datos de MetaQuotes (%APPDATA%\\Roaming\\MetaQuotes\\) para evitar bloqueos temporales al escribir logs o archivos de base de datos.34

## **5\. Workflow de Desarrollo en macOS → Ejecución en VPS**

La implementación de un flujo de trabajo moderno y estructurado evita tener que programar de manera remota sobre el entorno gráfico lento del VPS, permitiendo al desarrollador trabajar localmente en su entorno nativo de macOS.

                 │  
                 ▼  (rsync o Git Push en rama 'deploy')

                 │  
                 ▼  (MetaEditor CLI via Wine o SSH)

                 │  
                 ▼

### **Configuración del IDE en macOS para MQL5**

El desarrollador en macOS puede configurar **Visual Studio Code** instalando la extensión **MQL Tools** o **MQL Clangd**.41 Estas herramientas analizan la sintaxis MQL5 nativa mapeando las cabeceras estándar mediante la configuración de un archivo settings.json local 41:

JSON  
{  
    "mql\_tools.Metaeditor.Include5Dir": "/Users/\<usuario\>/MQL5/Include",  
    "mql\_tools.Compile.RunTaskOnSuccess": "Sync\_Files"  
}

### **Sincronización Automática con rsync**

Para automatizar la subida de los archivos de código fuente (.mq5, .mqh) desde el ordenador macOS local hacia la ruta de datos del terminal en el VPS Windows, se descarta el uso de servicios en la nube comerciales por su lentitud. Se recomienda implementar un script continuo usando rsync configurado con la extensión **Save and Run** de VS Code para disparar la transferencia con cada guardado 43:

JSON  
"saveAndRun": {  
    "commands":  
}

### **Compilación Remota Desatendida en la VPS**

El binario ejecutable final (.ex5) debe compilarse directamente en el entorno nativo de Windows para evitar errores de enlace estático de librerías de sistema.45 Esto se puede realizar de forma automatizada enviando una llamada remota de compilación vía SSH al compilador CLI de MetaEditor 45:

Bash  
\# Compilación del archivo.mq5 transferido mediante llamada remota de SSH  
ssh Administrator@\<IP\_VPS\> "powershell.exe \-Command & 'C:\\Program Files\\MetaTrader 5\\metaeditor64.exe' /compile:'C:\\Users\\Administrator\\AppData\\Roaming\\MetaQuotes\\Terminal\\\<GUID\>\\MQL5\\Experts\\MiEA.mq5' /log:'C:\\Users\\Administrator\\AppData\\Roaming\\MetaQuotes\\Terminal\\\<GUID\>\\MQL5\\Experts\\compile.log'"

El script en macOS lee remotamente el archivo compile.log resultante para validar si existen errores de sintaxis o advertencias en el código fuente.45

### **Ejecución en el Strategy Tester de la VPS**

Para ejecutar optimizaciones masivas en el hardware dedicado del VPS, se puede configurar el Strategy Tester desatendido mediante un archivo .ini sin necesidad de inicializar la interfaz visual de MT5 41:

Bash  
\# Lanzamiento del Strategy Tester desatendido desde el terminal  
ssh Administrator@\<IP\_VPS\> "C:\\Program Files\\MetaTrader 5\\terminal64.exe /config:C:\\Users\\Administrator\\Desktop\\tester\_config.ini"

El archivo tester\_config.ini debe contener la parametrización completa del backtesting 41:

Ini, TOML  
Expert\=MiEA.ex5  
Symbol\=EURUSD  
Period\=H1  
Deposit\=10000  
Currency\=USD  
Model\=4 ; Representa "Every tick based on real ticks"  
ExecutionMode\=0 ; Representa retardo de red cero  
FromDate\=2026.01.01  
ToDate\=2026.06.01  
Report\=MiEA\_Report  
ReplaceReport\=1  
ShutdownWhenFinished\=1

## **6\. Acceso Remoto y Control desde macOS**

Para controlar la infraestructura en la nube sin comprometer los ciclos de reloj de la máquina virtual con procesos gráficos innecesarios se deben optimizar los protocolos de red.32

### **Microsoft Remote Desktop (RDP) para Mac**

Es la aplicación oficial y más estable para conectar con la VPS desde macOS.2 Para minimizar la latencia de refresco y el lag de pantalla se deben ajustar las opciones del perfil de conexión en Mac 46:

* En la pestaña **Display**: Establecer una profundidad de color fija de **High Color (16 bit)** y fijar una resolución de escritorio baja (como ![][image20]), evitando escalar la visualización a resolución Retina nativa.  
* En la pestaña **Local Resources**: Desactivar de forma estricta la redirección de impresoras, micrófonos y audio.46 Mantener activa exclusivamente la redirección del portapapeles (*clipboard*) para permitir la transferencia manual rápida de archivos ejecutables compilados locales hacia el VPS.2

### **Protocolo Parsec para Monitoreo de Alta Fidelidad**

Para estrategias que dependen de la monitorización visual continua de flujos de ticks rápidos donde el RDP convencional presenta un retardo excesivo (lag promedio de ![][image21]), se puede utilizar **Parsec**.46 Parsec implementa un protocolo UDP de baja latencia llamado **BUD**, que aprovecha la codificación por hardware de la GPU en el VPS y descodifica nativamente en el chip Apple Silicon de manera óptima, reduciendo el lag de refresco visual a solo ![][image22].46

### **Túneles de SSH Seguro**

Para evitar el uso de cualquier capa gráfica, se recomienda habilitar el servidor OpenSSH integrado de Windows Server. Mediante un túnel SSH, se pueden realizar tareas administrativas, monitorizar el uso de recursos y compilar los archivos de manera inmediata y segura desde el terminal nativo de macOS:

Bash  
\# Establecer un túnel SSH seguro para retransmitir servicios de base de datos  
ssh \-L 5432:127.0.0.1:5432 Administrator@\<IP\_VPS\>

## **7\. Telemetría, Alertas y Monitoreo Activo**

Un sistema algorítmico maduro en producción debe contar con múltiples capas de monitorización automatizada para notificar inmediatamente cualquier comportamiento anómalo de los EAs o desconexiones del sistema.14

          │  
          ├── (Validación de Tick / Latido cada 60s) ──\> ──\> \[Notificación Móvil\]  
          │

          │  
          └── (Fallo de Proceso o Caída de Red) ──────\> \[Healthchecks.io\] ───\>

### **Clase en MQL5 para Envío de Heartbeats a Telegram**

La monitorización proactiva exige que el EA notifique de manera regular su estado operativo. Para ello, se integra una clase en el código del EA que realiza peticiones HTTP a la API de bots de Telegram 48:

Fragmento de código  
//+------------------------------------------------------------------+  
//| Clase de Monitoreo para Telegram (TelegramTelemetry.mqh)        |  
//+------------------------------------------------------------------+  
\#property copyright "Systems Architect"  
\#property version   "1.00"

class CTelegramTelemetry  
  {  
private:  
   string            m\_bot\_token;  
   string            m\_chat\_id;  
   datetime          m\_last\_ping;  
   int               m\_ping\_interval; // En segundos

public:  
                     CTelegramTelemetry(string bot\_token, string chat\_id, int interval)  
     {  
      m\_bot\_token \= bot\_token;  
      m\_chat\_id \= chat\_id;  
      m\_ping\_interval \= interval;  
      m\_last\_ping \= 0;  
     }

   bool              SendPing(string msg)  
     {  
      string url \= "https://api.telegram.org/bot" \+ m\_bot\_token \+ "/sendMessage";  
      string headers \= "Content-Type: application/x-www-form-urlencoded\\r\\n";  
      string post\_data \= "chat\_id=" \+ m\_chat\_id \+ "\&text=" \+ UrlEncode(msg) \+ "\&parse\_mode=Markdown";  
        
      char post\_char;  
      char result\_char;  
      string result\_headers;  
        
      StringToCharArray(post\_data, post\_char, 0, WHOLE\_ARRAY, CP\_UTF8);  
        
      int res \= WebRequest("POST", url, headers, 5000, post\_char, result\_char, result\_headers);  
      return (res \== 200);  
     }

   void              Heartbeat()  
     {  
      datetime current\_time \= TimeLocal();  
      if(current\_time \- m\_last\_ping \>= m\_ping\_interval)  
        {  
         string msg \= "\*\*\\n" \+  
                      "Estado: \`ACTIVO\`\\n" \+  
                      "Cuenta: \`" \+ IntegerToString(AccountInfoInteger(ACCOUNT\_LOGIN)) \+ "\`\\n" \+  
                      "Broker: \`" \+ AccountInfoString(ACCOUNT\_SERVER) \+ "\`\\n" \+  
                      "Ping Red: \`" \+ IntegerToString(TerminalInfoInteger(TERMINAL\_PING\_LAST)) \+ " ms\`";  
         if(SendPing(msg))  
           {  
            m\_last\_ping \= current\_time;  
           }  
        }  
     }

private:  
   string            UrlEncode(string text)  
     {  
      string encoded \= "";  
      uchar src;  
      StringToCharArray(text, src);  
      int size \= ArraySize(src) \- 1;  
      for(int i \= 0; i \< size; i++)  
        {  
         if((src\[i\] \>= 'A' && src\[i\] \<= 'Z') || (src\[i\] \>= 'a' && src\[i\] \<= 'z') || (src\[i\] \>= '0' && src\[i\] \<= '9'))  
           {  
            encoded \+= CharToString(src\[i\]);  
           }  
         else  
           {  
            encoded \+= StringFormat("%%%02X", src\[i\]);  
           }  
        }  
      return encoded;  
     }  
  };

### **Monitoreo Externo mediante Healthchecks.io (Dead Man's Switch)**

El propio EA debe realizar una petición HTTP tipo GET a una URL de **Healthchecks.io** o **UptimeRobot** en su ciclo periódico OnTimer.50 Si el servidor de la VPS colapsa por completo o la red de datos se interrumpe, la VPS dejará de enviar el ping a Healthchecks.io.12 Al transcurrir el periodo de gracia establecido, Healthchecks.io interpretará que el sistema operativo ha colapsado y enviará notificaciones instantáneas a los canales del operador.50

### **Notificaciones Push de MT5 Directas a iOS**

MetaTrader 5 integra un canal de comunicación nativo y redundante con la aplicación móvil en iOS a través de la infraestructura de MetaQuotes:

1. En el terminal de MT5 de la VPS, navegar a Tools \-\> Options \-\> Notifications.  
2. Marcar la opción **"Enable Push Notifications"** y registrar el **MetaQuotes ID** único provisto por el menú de configuración de la aplicación de MT5 instalada en el iPhone.  
3. Desde la lógica interna del EA, se invoca de manera asíncrona la función nativa de notificación ante eventos críticos:  
   Fragmento de código  
   SendNotification("ALERTA CRÍTICA: Desconexión de pasarela detectada. Forzando cierre.");

## **8\. Sistema de Auto-recuperación ante Fallos (Auto-recovery)**

Un entorno de trading profesional asume que el software eventualmente experimentará errores críticos de ejecución. La robustez operativa se define por la capacidad del sistema para volver a un estado estable sin intervención humana.32

### **Script de Watchdog en PowerShell**

Se debe programar un script persistente en la VPS que verifique el estado del proceso de MT5 cada 15 segundos, reiniciándolo automáticamente si detecta un cuelgue o un cierre del proceso 32:

PowerShell  
\# Watchdog\_MT5.ps1  
\# Monitoriza terminal64.exe y lo levanta inmediatamente tras cierres inesperados.

$ProcessName \= "terminal64"  
$ExecutablePath \= "C:\\Program Files\\MetaTrader 5\\terminal64.exe"  
$LogPath \= "C:\\watchdog\\watchdog\_log.txt"

function Write-Log ($Msg) {  
    $Date \= Get-Date \-Format "yyyy-MM-dd HH:mm:ss"  
    $FullMsg \= "$Date \- $Msg"  
    Add-Content \-Path $LogPath \-Value $FullMsg  
    Write-Host $FullMsg  
}

Write-Log "Iniciando Watchdog de MetaTrader 5..."

while ($true) {  
    $Process \= Get-Process \-Name $ProcessName \-ErrorAction SilentlyContinue  
      
    if (\-not $Process) {  
        Write-Log "ALERTA: terminal64.exe no está corriendo. Iniciando proceso..."  
        try {  
            Start-Process \-FilePath $ExecutablePath \-ArgumentList "/profile:Default" \-WindowStyle Normal  
            Write-Log "Proceso lanzado con éxito."  
        }  
        catch {  
            Write-Log "ERROR CRÍTICO: No se pudo arrancar terminal64.exe. Detalle: $\_"  
        }  
    }  
    else {  
        \# Validar si el proceso está congelado en segundo plano  
        if ($Process.Responding \-eq $false) {  
            Write-Log "ALERTA: El proceso terminal64.exe ha dejado de responder. Forzando detención..."  
            Stop-Process \-Name $ProcessName \-Force  
            Start-Sleep \-Seconds 5  
        }  
    }  
    Start-Sleep \-Seconds 15  
}

Este script se programa en el Task Scheduler de Windows para ejecutarse en el arranque del sistema operativo (At system startup) con los privilegios del usuario administrador de la VPS.52

### **Reinicio Automático de la VPS mediante API de Proveedor**

Si la máquina virtual sufre una interrupción total del kernel que bloquea incluso el programador de tareas de Windows, el sistema de monitorización local queda inoperante. En este escenario, un script en la máquina macOS local (u otro servidor secundario de monitorización) detecta la caída prolongada de pings en Healthchecks.io y ejecuta de forma automatizada una llamada a la API del proveedor de VPS para forzar un reinicio a nivel de hipervisor:

Bash  
\# Ejemplo de llamada de reinicio por hardware a través de la API de Vultr  
curl \-H "API-Key: TU\_API\_KEY\_AQUÍ" \-X POST "https://api.vultr.com/v2/instances/INSTANCE\_ID/reboot"

### **Gestión de Estado Persistente en Base de Datos SQLite Nativa**

Para que el EA reanude su lógica operativa de forma exacta tras experimentar un reinicio de emergencia sin perder la trazabilidad de las órdenes lógicas, se descarta el uso de variables globales del terminal (GlobalVariables), ya que éstas residen en memoria volátil y solo se escriben en disco (gvars.dat) cuando el terminal se cierra de forma ordenada. Si la VPS se congela o experimenta un reinicio forzado, las GlobalVariables de las últimas horas se perderán, creando el riesgo de dobles aperturas de órdenes.  
MetaTrader 5 incorpora de forma nativa soporte para bases de datos transaccionales **SQLite**.53 Este motor escribe transacciones directamente en el disco duro SSD de forma inmediata mediante transacciones ACID seguras.53

Fragmento de código  
//+------------------------------------------------------------------+  
//| Almacenamiento de Estado del EA en SQLite (StatePersistence.mqh) |  
//+------------------------------------------------------------------+  
\#include \<Database.mqh\>

int db\_handle \= INVALID\_HANDLE;  
string db\_name \= "EA\_State.sqlite";

bool OpenAndInitDatabase()  
  {  
   // El archivo de la base de datos se guarda en MQL5/Files/ \[53, 56\]  
   db\_handle \= DatabaseOpen(db\_name, DATABASE\_OPEN\_READWRITE | DATABASE\_OPEN\_CREATE);  
   if(db\_handle \== INVALID\_HANDLE)  
     {  
      Print("Error al inicializar SQLite: ", GetLastError());  
      return false;  
     }  
     
   // Tabla para persistir el ID único de la estrategia, volumen acumulado y estado lógico  
   string query \= "CREATE TABLE IF NOT EXISTS ea\_persistence ("  
                  "strategy\_key TEXT PRIMARY KEY,"  
                  "accumulated\_lot REAL,"  
                  "current\_logic\_state TEXT"  
                  ");";  
                    
   if(\!DatabaseExecute(db\_handle, query))  
     {  
      Print("Error en creación de esquema SQLite: ", GetLastError());  
      DatabaseClose(db\_handle);  
      return false;  
     }  
   return true;  
  }

bool PersistState(string key, double lot, string state)  
  {  
   string query \= StringFormat("INSERT OR REPLACE INTO ea\_persistence (strategy\_key, accumulated\_lot, current\_logic\_state) "  
                               "VALUES ('%s', %f, '%s');", key, lot, state);  
   return DatabaseExecute(db\_handle, query);  
  }

## **9\. Backup y Plan de Recuperación ante Desastres (Disaster Recovery)**

Para garantizar la continuidad del negocio y estar preparados en caso de una caída permanente de hardware en el nodo del centro de datos del proveedor de VPS, se debe implementar una rutina de copias de seguridad automatizadas y fuera del sitio (*off-site backups*).14

\[MQL5 / Config /.ini / Profiles\]  
                │  
                ▼  (PowerShell ZIP Script cada 12 horas)

                │  
                ▼  (Upload Remoto a AWS S3 o OneDrive)

### **Script de Backup Automatizado de MetaTrader 5**

Se ejecuta un script de PowerShell programado cada 12 horas que empaqueta las carpetas de datos críticas de MT5 y las transfiere a un almacenamiento redundante 34:

PowerShell  
\# Backup\_MT5.ps1  
\# Empaqueta cabeceras, EAs, perfiles y base de datos SQLite, enviándolos a un bucket S3.

$TerminalDataPath \= "C:\\Users\\Administrator\\AppData\\Roaming\\MetaQuotes\\Terminal\\\<GUID\_TERMINAL\>\\"  
$BackupFolder \= "C:\\backups"  
$Timestamp \= Get-Date \-Format "yyyyMMdd\_HHmmss"  
$ArchiveName \= "$BackupFolder\\MT5\_Backup\_$Timestamp.zip"

if (\-not (Test-Path $BackupFolder)) {  
    New-Item \-Path $BackupFolder \-ItemType Directory | Out-Null  
}

Write-Host "Generando compresión de archivos críticos de MT5..."

\# Compresión omitiendo los logs de historial pesados para reducir tamaño  
Compress-Archive \-Path "$TerminalDataPath\*" \-DestinationPath $ArchiveName \-Force \-Exclude "\*.log"

\# Envío automatizado a un servicio externo (AWS S3) mediante el módulo AWS de PowerShell \[58\]  
Import-Module AWSPowerShell  
Write-S3Object \-BucketName "tu-bucket-backups-trading" \-File $ArchiveName \-Key "MT5\_Backup\_$Timestamp.zip" \-AccessKey "TU\_AWS\_ACCESS\_KEY" \-SecretKey "TU\_AWS\_SECRET\_KEY"

Write-Host "Copia de seguridad transferida correctamente."

### **Procedimiento de Recuperación Completa en \< 1 Hora (Disaster Recovery Checklist)**

Si el VPS principal colapsa de forma irrecuperable, se procede con la restauración sistemática del entorno en un nodo alternativo en frío:

1. \[ \] **Aprovisionar la Nueva VPS**: Crear una nueva instancia de Windows Server en un servidor alternativo (en el mismo centro de datos, ej. Equinix LD4).12  
2. \[ \] **Inicializar la Optimización**: Ejecutar el script automatizado para reconfigurar el plan de energía, priorización de servicios y desactivación de actualizaciones de Windows.32  
3. \[ \] **Instalar MT5**: Descargar el instalador nativo provisto por el broker Pepperstone.12  
4. \[ \] **Descargar y Extraer Backup**: Conectar al almacenamiento redundante S3 y descargar el archivo zip de respaldo más reciente. Extraer su contenido directamente en el directorio de datos del nuevo terminal de MT5.2  
5. \[ \] **Verificar Claves y Token de Licencias**: En caso de usar EAs protegidos comercialmente por el MQL5 Market, iniciar sesión en la cuenta MQL5 dentro de MT5 para reactivar las licencias correspondientes.  
6. \[ \] **Activar el Watchdog**: Desplegar el archivo Watchdog\_MT5.ps1 e inicializar la tarea del programador de tareas para asegurar el reinicio automático del servicio ante caídas.52  
7. \[ \] **Validación de Conectividad**: Confirmar que los gráficos muestren la recepción correcta de flujo de cotización en tiempo real con una latencia inferior a ![][image23] hacia el broker.12

## **10\. Costos y Matriz de Decisión Final**

La elección del entorno de producción óptimo para un operador algorítmico profesional exige evaluar las opciones en base al Costo Total de Propiedad (TCO) y la fiabilidad técnica del ecosistema.23

### **Análisis Comparativo del Costo Total Mensual (TCO \- 2026\)**

Se detallan a continuación los tres escenarios de inversión típicos para operar este flujo de trabajo:

* **Opción A: Virtualización Local (Parallels Desktop \+ Windows 11 ARM sobre Apple Silicon)**:  
  * Licencia anual Parallels Desktop Standard/Pro amortizada: ![][image24].2  
  * Licencia de sistema operativo Windows 11 Pro amortizada: ![][image25].2  
  * Gasto energético estimado del Mac en funcionamiento continuo 24/5: ![][image26].  
  * **Costo Total Opción A**: ![][image27].  
* **Opción B: VPS Windows Nube Generalista (AWS Lightsail Medium Windows)**:  
  * Instancia base Windows (2 vCPU / 4 GB RAM / 80 GB SSD): ![][image28].20  
  * Snapshot de almacenamiento redundante (200 GB históricos): ![][image29].30  
  * Costo por transferencia de datos (egress y telemetría): ![][image30].30  
  * **Costo Total Opción B**: ![][image31].  
* **Opción C: VPS Premium de Baja Latencia Financiera (Beeks Financial Cloud o ForexVPS.net)**:  
  * Instancia optimizada co-ubicada con redundancia de hardware y backups sin límites de tráfico: ![][image32] (Precio fijo mensual bajo contrato recurrente sin costos variables de red o copias de seguridad).12

### **Matriz de Decisión Arquitectónica**

La siguiente matriz compara las tres alternativas en función de los requerimientos operativos de trading algorítmico profesional.

| Dimensión Técnica y Operativa | Opción A (Virtualización Local) | Opción B (VPS Nube General \- AWS) | Opción C (VPS Premium Financiero) |
| :---- | :---- | :---- | :---- |
| **Fiabilidad 24/5** | **Inaceptable**: Riesgo de caídas domésticas de energía, microcortes de red y suspensión por el cierre físico de la tapa del equipo.2 | **Alta**: Centros de datos estables, pero sujeto a colapsos si no se realiza un mantenimiento manual de la pila de red. | **Máxima**: SLA del ![][image33] nativo. Pila de software y parches de sistema depurados de fábrica para trading.14 |
| **Latencia de Red** | **Deficiente**: Latencia típica residencial de ![][image34] a ![][image35].2 Provoca pérdidas por deslizamiento de precio y spreads desfavorables. | **Regular**: Latencia de ![][image8] a ![][image6]. No optimizado para trading de alta velocidad. | **Excelente**: Latencia inferior a ![][image36] consistente, libre de jitter, hacia los servidores principales de liquidez.12 |
| **Facilidad de Mantenimiento** | **Mala**: El desarrollador debe gestionar parches de compatibilidad de emulación ARM64 y actualizaciones intrusivas de Parallels.9 | **Media**: Requiere configuración manual a bajo nivel de las políticas del SO, firewall, balanceadores y seguridad corporativa. | **Excelente**: El VPS se aprovisiona listo para operar, con terminales de brokers preinstalados y soporte especialista.2 |
| **Escalabilidad** | **Baja**: El rendimiento se degrada rápidamente si se ejecutan más de dos instancias de MT5 concurrentes bajo emulación Prism.2 | **Excelente**: Escalado vertical instantáneo en consola, a costa de un incremento exponencial en la factura mensual. | **Excelente**: Admite el despliegue de múltiples terminales con asignaciones físicas de hardware dedicadas sin pérdida de rendimiento. |

### **Impacto de la Latencia en el Rendimiento Financiero (Slippage Model)**

El impacto financiero del retardo en la transmisión de órdenes se puede modelar de forma matemática. El coste promedio de deslizamiento de precios (![][image37]) en una orden de mercado está definido por la volatilidad instantánea del activo (![][image38]), la latencia de red de ida y vuelta (![][image39]), y un factor de profundidad de liquidez (![][image40]):  
![][image41]  
En un entorno local (Opción A) con una conexión de red residencial típica (![][image42]), la micro-variabilidad de spreads y el retraso en la ejecución añaden de media entre ![][image43] y ![][image44] pips de coste de transacción fantasma en cada orden ejecutada.  
Por el contrario, con una VPS co-ubicada físicamente en Equinix LD4 (Opción C) donde el ping es óptimo (![][image45]), el coste de deslizamiento tiende a cero. Para un EA que opere un volumen mensual modesto de 100 lotes estándar en EUR/USD, un deslizamiento de solo 0.5 pips representa una fuga silenciosa de capital de **$500.00 USD mensuales**, una cantidad que triplica el costo mensual de la infraestructura VPS de mayor categoría disponible en el mercado.22

### **Recomendación Técnica Final**

Para un desarrollador algorítmico profesional que trabaja en macOS (Apple Silicon), **la única solución estable, escalable y mantenible en producción es la implementación de un flujo de trabajo híbrido** 12:

1. **Entorno de Desarrollo**: Utilizar el procesador Apple Silicon de forma nativa para programar y realizar backtestings iniciales rápidos sobre macOS utilizando Visual Studio Code con extensiones de depuración.41  
2. **Entorno de Ejecución**: Desplegar el código mediante rsync o Git hacia una **VPS Premium de Grado Financiero (Beeks Financial Cloud o ForexVPS.net) co-ubicada físicamente en el mismo centro de datos de Equinix donde Pepperstone tenga alojado su servidor de ejecución**.12

Esta separación modular del flujo de trabajo aísla la lógica operativa en la nube de cualquier imprevisto de suministro o software local de macOS, permitiendo que las órdenes se ejecuten con latencias inferiores a un milisegundo y bajo un control de disponibilidad constante las 24 horas de la sesión de negociación.2

#### **Fuentes citadas**

1. Metatrader 5 For Mac: Complete Setup & Trading Guide \- Traze, acceso: junio 28, 2026, [https://traze.com/academy/broker-tools-and-features/metatrader-5-for-mac/](https://traze.com/academy/broker-tools-and-features/metatrader-5-for-mac/)  
2. How to Run MetaTrader 4 & 5 on macOS in 2026 (Plus the VPS Shortcut), acceso: junio 28, 2026, [https://newyorkcityservers.com/blog/metatrader-mac-install-vps-guide](https://newyorkcityservers.com/blog/metatrader-mac-install-vps-guide)  
3. Mt5 compatibility on macOS : r/Forex \- Reddit, acceso: junio 28, 2026, [https://www.reddit.com/r/Forex/comments/1qczrmj/mt5\_compatibility\_on\_macos/](https://www.reddit.com/r/Forex/comments/1qczrmj/mt5_compatibility_on_macos/)  
4. MetaTrader 5 Compatibility on MacBook Air M3 via Parallels Desktop \- MT5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/494485](https://www.mql5.com/en/forum/494485)  
5. Unable to load MT5 in MacWINE? \- Apple Communities, acceso: junio 28, 2026, [https://discussions.apple.com/thread/256236064](https://discussions.apple.com/thread/256236064)  
6. Fix Metatrader 4 or Metatrader 5 not working in Windows 11 on Mac with Apple silicon, acceso: junio 28, 2026, [https://kb.parallels.com/en/129408](https://kb.parallels.com/en/129408)  
7. Options for using Windows 11 with Mac® computers with Apple® M1®, M2™, and M3™ chips | Microsoft Support, acceso: junio 28, 2026, [https://support.microsoft.com/en-us/windows/experience/platform-variants/options-for-using-windows-11-with-mac-computers-with-apple-m1-m2-and-m3-chips](https://support.microsoft.com/en-us/windows/experience/platform-variants/options-for-using-windows-11-with-mac-computers-with-apple-m1-m2-and-m3-chips)  
8. bahadirumutiscimen/silicon-metatrader5: MetaTrader 5 ... \- GitHub, acceso: junio 28, 2026, [https://github.com/bahadirumutiscimen/silicon-metatrader5](https://github.com/bahadirumutiscimen/silicon-metatrader5)  
9. Windows 11 keeps crashing randomly on multiple machines \- Parallels Forums, acceso: junio 28, 2026, [https://forum.parallels.com/threads/windows-11-keeps-crashing-randomly-on-multiple-machines.369312/](https://forum.parallels.com/threads/windows-11-keeps-crashing-randomly-on-multiple-machines.369312/)  
10. Microsoft-authorized Windows 11 on Mac | Parallels Desktop, acceso: junio 28, 2026, [https://www.parallels.com/products/desktop/microsoft-authorized-solution-windows-11-arm/](https://www.parallels.com/products/desktop/microsoft-authorized-solution-windows-11-arm/)  
11. Sudden shut down of windows 11 | Parallels Forums, acceso: junio 28, 2026, [https://forum.parallels.com/threads/sudden-shut-down-of-windows-11.369850/](https://forum.parallels.com/threads/sudden-shut-down-of-windows-11.369850/)  
12. Pepperstone VPS – Professional Trading with 1ms Latency \- Forex VPS, acceso: junio 28, 2026, [https://newyorkcityservers.com/pepperstone-vps](https://newyorkcityservers.com/pepperstone-vps)  
13. Best VPS Locations for Low Latency Trading in 2026 \- ForexVPS, acceso: junio 28, 2026, [https://www.forexvps.net/resources/best-vps-location-low-latency-trading/](https://www.forexvps.net/resources/best-vps-location-low-latency-trading/)  
14. MassiveGRID Forex VPS vs. ForexVPS.net vs. BeeksFX: An Honest Comparison, acceso: junio 28, 2026, [https://massivegrid.com/blog/massivegrid-vs-forexvps-vs-beeksfx/](https://massivegrid.com/blog/massivegrid-vs-forexvps-vs-beeksfx/)  
15. ForexVPS vs Beeks Financial Cloud: Best Trading VPS, acceso: junio 28, 2026, [https://www.forexvps.net/resources/forexvps-vs-beeks-financial-cloud/](https://www.forexvps.net/resources/forexvps-vs-beeks-financial-cloud/)  
16. Best Forex VPS for Trading in 2026 \- Cybernews, acceso: junio 28, 2026, [https://cybernews.com/vps/best-forex-vps/](https://cybernews.com/vps/best-forex-vps/)  
17. Top VPS Providers for Algorithmic Trading: 2026 Comparison \- ForexVPS, acceso: junio 28, 2026, [https://www.forexvps.net/resources/best-vps-for-algorithmic-trading/](https://www.forexvps.net/resources/best-vps-for-algorithmic-trading/)  
18. Forex VPS Hosting | Trading FXVPS, acceso: junio 28, 2026, [https://tradingfxvps.com/services/forex-vps-plan/](https://tradingfxvps.com/services/forex-vps-plan/)  
19. Contabo VPS Hosting Plans 2026 \- Pricing, Reviews & Features, acceso: junio 28, 2026, [https://www.comparevps.com/hosting/contabo](https://www.comparevps.com/hosting/contabo)  
20. Amazon Lightsail Pricing, acceso: junio 28, 2026, [https://aws.amazon.com/lightsail/pricing/](https://aws.amazon.com/lightsail/pricing/)  
21. Amazon Lightsail Pricing: 2026 Guide to True Total Cost \- CloudBurn, acceso: junio 28, 2026, [https://cloudburn.io/blog/amazon-lightsail-pricing](https://cloudburn.io/blog/amazon-lightsail-pricing)  
22. Best Forex VPS for Scalping: 8 Providers Compared (2026), acceso: junio 28, 2026, [https://www.vpsforextrader.com/blog/forex-vps-scalping-comparison-2026/](https://www.vpsforextrader.com/blog/forex-vps-scalping-comparison-2026/)  
23. Forex VPS Hosting Guide 2026: Choosing a VPS for MT4 and MT5 Trading, acceso: junio 28, 2026, [https://myforexvps.com/forex-vps-explained-choosing-the-right-vps-for-mt4-mt5-in-2026/](https://myforexvps.com/forex-vps-explained-choosing-the-right-vps-for-mt4-mt5-in-2026/)  
24. ForexVPS vs TradingFXVPS: A Full Comparison for Traders, acceso: junio 28, 2026, [https://www.forexvps.net/resources/forexvps-vs-tradingfxvps/](https://www.forexvps.net/resources/forexvps-vs-tradingfxvps/)  
25. Best Forex VPS Providers in 2025: Low-Latency Options for MT4 Traders \- MassiveGRID, acceso: junio 28, 2026, [https://massivegrid.com/blog/best-forex-vps-providers-in-2025/](https://massivegrid.com/blog/best-forex-vps-providers-in-2025/)  
26. Best Budget-Friendly Forex VPS Providers in 2026: Cheap, Fast, and Actually Reliable for EA Traders, acceso: junio 28, 2026, [https://www.vpsforextrader.com/blog/budget-friendly-forex-vps-providers/](https://www.vpsforextrader.com/blog/budget-friendly-forex-vps-providers/)  
27. Best Windows VPS for Forex Trading (2026) | Setup & Specs Guide, acceso: junio 28, 2026, [https://tradingfxvps.com/windows-vps-for-forex-trading-2026-complete-setup-guide/](https://tradingfxvps.com/windows-vps-for-forex-trading-2026-complete-setup-guide/)  
28. The Best Value Cloud VPS On Earth \- Contabo, acceso: junio 28, 2026, [https://contabo.com/en-us/vps/](https://contabo.com/en-us/vps/)  
29. Amazon AWS vs Amazon Lightsail: performance, features and prices | VPSBenchmarks, acceso: junio 28, 2026, [https://www.vpsbenchmarks.com/compare/aws\_vs\_lightsail](https://www.vpsbenchmarks.com/compare/aws_vs_lightsail)  
30. AWS Lightsail vs Traditional VPS: True Cost Comparison for 2026 | MassiveGRID Blog, acceso: junio 28, 2026, [https://massivegrid.com/blog/aws-lightsail-vs-traditional-vps-cost-comparison/](https://massivegrid.com/blog/aws-lightsail-vs-traditional-vps-cost-comparison/)  
31. AWS Lightsail Pricing (2026): Complete Plans & Comparisons, acceso: junio 28, 2026, [https://kuberns.com/blogs/aws-lightsail-pricing-your-comprehensive-guide/](https://kuberns.com/blogs/aws-lightsail-pricing-your-comprehensive-guide/)  
32. How to Optimize Your Windows VPS for Maximum Forex Trading Performance, acceso: junio 28, 2026, [https://massivegrid.com/blog/optimize-windows-vps-forex-trading-performance/](https://massivegrid.com/blog/optimize-windows-vps-forex-trading-performance/)  
33. Optimizing MetaTrader on Your InterServer VPS, acceso: junio 28, 2026, [https://www.interserver.net/tips/kb/optimizing-metatrader-on-your-interserver-vps/](https://www.interserver.net/tips/kb/optimizing-metatrader-on-your-interserver-vps/)  
34. MT5 on Windows 11 VPS Setup \+ Optimisation Guide. \- VM6 Networks, acceso: junio 28, 2026, [https://www.vm6.co.uk/blog/2026/01/18/mt5-on-windows-11-vps-setup-optimisation-guide/](https://www.vm6.co.uk/blog/2026/01/18/mt5-on-windows-11-vps-setup-optimisation-guide/)  
35. Enhancing MT4/MT5 Performance with Forex VPS Integration | FXVPS, acceso: junio 28, 2026, [https://fxvps.biz/blog/enhancing-mt4-mt5-performance-with-forex-vps-integration/](https://fxvps.biz/blog/enhancing-mt4-mt5-performance-with-forex-vps-integration/)  
36. Set Up MT4/MT5 on a Windows VPS (Step-by-Step) \- HostStage, acceso: junio 28, 2026, [https://www.host-stage.net/case-study/forex/mt4-mt5-vps-setup-guide/](https://www.host-stage.net/case-study/forex/mt4-mt5-vps-setup-guide/)  
37. How to Autostart Metatrader 4/5 after a VPS reboot? \- Dipgate, acceso: junio 28, 2026, [https://dipgate.com/index.php?rp=/knowledgebase/7/How-to-Autostart-Metatrader-4or5-after-a-VPS-reboot.html](https://dipgate.com/index.php?rp=/knowledgebase/7/How-to-Autostart-Metatrader-4or5-after-a-VPS-reboot.html)  
38. How do I automatically restart MetaTrader apps after the VPS restart? \- Pepperstone, acceso: junio 28, 2026, [https://pepperstone.com/en/support/how-do-i-automatically-restart-metatrader-apps-after-the-vps-restart/](https://pepperstone.com/en/support/how-do-i-automatically-restart-metatrader-apps-after-the-vps-restart/)  
39. How to automatically restart MT4 MT5 when crashing \- Knowledge Base \- Hyonix, acceso: junio 28, 2026, [https://howto.hyonix.com/article/how-to-automatically-restart-mt4-mt5-when-crashing/](https://howto.hyonix.com/article/how-to-automatically-restart-mt4-mt5-when-crashing/)  
40. How to Install and Run MetaTrader 5 (MT5) as a Windows Service | AlwaysUp, acceso: junio 28, 2026, [https://www.coretechnologies.com/products/AlwaysUp/Apps/InstallMetaTrader5WindowsService.html](https://www.coretechnologies.com/products/AlwaysUp/Apps/InstallMetaTrader5WindowsService.html)  
41. MQL Clangd \- Visual Studio Marketplace, acceso: junio 28, 2026, [https://marketplace.visualstudio.com/items?itemName=ngSoftware.mql-clangd](https://marketplace.visualstudio.com/items?itemName=ngSoftware.mql-clangd)  
42. MQL Tools \- Visual Studio Marketplace, acceso: junio 28, 2026, [https://marketplace.visualstudio.com/items?itemName=L-I-V.mql-tools](https://marketplace.visualstudio.com/items?itemName=L-I-V.mql-tools)  
43. thisboyiscrazy/vscode-rsync: rsync extension for visual studio code \- GitHub, acceso: junio 28, 2026, [https://github.com/thisboyiscrazy/vscode-rsync](https://github.com/thisboyiscrazy/vscode-rsync)  
44. visual studio code \- Run rsync on every save in VSCode \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/65203784/run-rsync-on-every-save-in-vscode](https://stackoverflow.com/questions/65203784/run-rsync-on-every-save-in-vscode)  
45. Compile MQ5 file with VS Code extension on linux \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/76391990/compile-mq5-file-with-vs-code-extension-on-linux](https://stackoverflow.com/questions/76391990/compile-mq5-file-with-vs-code-extension-on-linux)  
46. Parsec vs RDP vs Rustdesk: How Do Remote Desktop Tools Stack Up? \- QuantVPS, acceso: junio 28, 2026, [https://www.quantvps.com/blog/parsec-vs-rdp-vs-rustdesk](https://www.quantvps.com/blog/parsec-vs-rdp-vs-rustdesk)  
47. Troubleshooting Lag, Latency and Quality Issues \- Parsec support, acceso: junio 28, 2026, [https://support.parsec.app/hc/en-us/articles/32381352822804-Troubleshooting-Lag-Latency-and-Quality-Issues](https://support.parsec.app/hc/en-us/articles/32381352822804-Troubleshooting-Lag-Latency-and-Quality-Issues)  
48. Send alert on Telegram from MT5 Indicator \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/491715](https://www.mql5.com/en/forum/491715)  
49. Send alert signal to telegram \- MQL4 programming forum \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/338070](https://www.mql5.com/en/forum/338070)  
50. Claude Code Heartbeat: automated reminders via Telegram \- GitHub Gist, acceso: junio 28, 2026, [https://gist.github.com/chrismdp/64c2947fbd1e8b640aa3036412995209](https://gist.github.com/chrismdp/64c2947fbd1e8b640aa3036412995209)  
51. Powershell script to check if service is started, if not then start it \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/35064964/powershell-script-to-check-if-service-is-started-if-not-then-start-it](https://stackoverflow.com/questions/35064964/powershell-script-to-check-if-service-is-started-if-not-then-start-it)  
52. Simple Windows network Watchdog – restart network or whole machine if IP address is not reachable | Luka Manojlovic, acceso: junio 28, 2026, [https://luka.manojlovic.net/2025/01/15/simple-windows-network-watchdog-restart-network-or-whole-machine-if-ip-address-is-not-reachable/](https://luka.manojlovic.net/2025/01/15/simple-windows-network-watchdog-restart-network-or-whole-machine-if-ip-address-is-not-reachable/)  
53. DatabaseOpen \- Working with databases \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/database/databaseopen](https://www.mql5.com/en/docs/database/databaseopen)  
54. MetaTrader 5 build 2340 simplifies working with SQLite and Python — algorithmic trading increased accessibility \- News, acceso: junio 28, 2026, [https://www.metatrader5.com/en/news/2127](https://www.metatrader5.com/en/news/2127)  
55. dingmaotu/mql-sqlite3: SQLite3 binding for the MQL language (both 32bit MT4 and 64bit MT5) \- GitHub, acceso: junio 28, 2026, [https://github.com/dingmaotu/mql-sqlite3](https://github.com/dingmaotu/mql-sqlite3)  
56. Import from file share to OneDrive for Business with PowerShell \- ShareGate help, acceso: junio 28, 2026, [https://help.sharegate.com/en/articles/10236383-import-from-file-share-to-onedrive-for-business-with-powershell](https://help.sharegate.com/en/articles/10236383-import-from-file-share-to-onedrive-for-business-with-powershell)  
57. Forex VPS Providers Compared: Latency, RAM & Pricing (2026), acceso: junio 28, 2026, [https://www.vpsforextrader.com/blog/best-forex-vps-providers-2026/](https://www.vpsforextrader.com/blog/best-forex-vps-providers-2026/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEUAAAAWCAYAAACWl1FwAAAAj0lEQVR4Xu3UPQrCQBRF4edPEUHSBGzcQPbiOtyTuAtTu4Ig2KUVCwsbwcLKFB5JEbjgAuTdD04zt52ZCDMzs3+w0YPM9vSmWoeMjvSklQ7ZzKmjKy1kS6ekO51oKls6a3pRo0Nm38+zp50ONt6Ygw4WsaQbtTSRLb0ZnelChWwWw5N6UKWDRWz1wMzMfvsAuH8SIA4GIKcAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGcAAAAWCAYAAADdP4KdAAAAuklEQVR4Xu3TzwoBUQCF8aukbGxsKVt7S9lbKc8gT6A8gJXyAlYewEPY2pM8CQv5czQzGSdZuVK+X301c2Z2txsCAAAAgA9oqrqPLxR8QDwNdVUXdUifh/kfcsqq5SPiuR+KW6mTqtl+tHdE1vUhVVXnkNykrPbTH/gJRR/wPdPwuB1L++Y6PiCetZrk3uchOaR+bsuMVclHxDPzIbUJySGNVE9t1f7pD0T37iZU1ELt1MC+AQAAAH/qBinKGzptkVQMAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEUAAAAWCAYAAACWl1FwAAAAtUlEQVR4Xu3SvQkCQRiE4U8QwcTEVMHU3FDMjQRrECsQLMBIsAEjC7AIU3PlsBINxJ+R3cO9QYwM5Lt54AVvbqP1zEREROQPdVGbxw8qPHjUQQ90R+f4e5oeSNRRj0ePXpfBduiKWrRf6NmtIQ9RE90sfDl5/cKJkqvyUAZLe38NW3rHBjx4tEeL5Hlt4XLGyZaboxqPHq14iA4WLmeGRuiIToUTjn375xtogzI0oXciIiLyE0/yLxs64k/WOAAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFMAAAAWCAYAAAC8J6DfAAADV0lEQVR4Xu2XSchOYRTHj1lCyCzsZAopFrL4IrOQYSErsiAlUUQ2SFkoQ7GgLCSZFhaGjCWUIQuzZCFE5iLzeP6e57zvef/vc9/7+RY27q/+fe/5n3Of+9zzPfc+94oUFBQU/BcMUW1RzXLeavf7rxmseq36pbqkaleZLnFSQs1b1TzK5XFQwrF3VK0oZ2DMZ6rvqg2US/FKwpimb6qXLr+T8pAH8RpVC9XcGO9Q3XU1b6JveiehVx9i/EM12YoXqLZaoOyRUDTUeQBes/h7doxflNOZ4BjU9opxkxh3K1UEDqmeuhjzwIXUh1SjPLdVncn7ImFFMhjHNxN0iv5l8sEwcedOTYS946rDLgZHJdRMIZ85r3pC3kZJn7NpwhtPXgqeL4M5MKjvy6YyU7KbeY58o85+4EJ5Ijw53HaIcSJjQPSeOy8FaraTNyL6xmaKDXgP2EzA82WymrmXzUhWM8+Sn8sqCQdOdF4P1W4XgzoJddfI99gtzQ/03tGfHuOvMWbymmTk1WU1E9rEiQTWzNOcqMU0CQelniXMCQm1AznhwE6JmqXk2+RWxDirGVk+k1d3gQ1ljJSPM92TsAAYm+8pTmSB5xh2XOxOoynH2Iq7yglilIS6xeS3jz52W5DVjCyfyau7yEakp5TvCq8uvkga0EwDtzQOPMIJxyepfXsbfSSMtYT8jtFfF+OsZmT5TF7dFTYStFWdkfRYDW4mSA1o4DXjAJsZNJIwzkrysSLgz4mxbXBMrXl48upusaFMYCNyU6rHqnczcVvb7WbY5EaSj3fB9eQ9ppjBOFm7ub1rYpJ8AQDeTzYT5DUTL/PMQzYiw6V6rHptQDMkPRHz/MN4uWqhiwGeLdtc3FK1yMUA/6wb5GEsf86uFBvwlrGZAK84PF8Dd8d7NiV9PjBfqnN5r0b4MvwDivA5ZQyK3jHnYUOyBrPGuTrz+jsPq5snh9h/dQGswH0uniTVx9UCG8lHNiX4qSZjbHwWcg4+P5b6RZ+fvd0l7B+leXaQcCEw7FvXrzbADfRq7OqmSnqHt5W4X8LF7apMl0DuvoT3QtS3rkzngndhHIe7AX9xoc0rKspcV7VRfZZQi29u/F3ri6Lnhec7PkWx2h+pxpZLCwoKCgoK/jG/AVtJK3FLPa61AAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFMAAAAWCAYAAAC8J6DfAAADPklEQVR4Xu2XS8hNURTHlzeFpFAkJfJISBhJn2eRopDHQMRAGVCKyABDlCgpj4lkQFGSgVcJ5TESYsL35S2v8n6z/vZe313f/+5zz7nfwMT51b9793+ts+866+x7zj4iJSUlJf8Fo1W7VPOdt8l9r5tRqteq36qrqh4tw80clZDzVbWeYlmg0EbVatUS1SLVQtWCKOObao2qj6qLaqqqycVTvJJQj+m76qWL76c45MF4i6qTalkc71PddTlvom96J6FXH+P4p2qWJa9U7baBclhC0hjnAXjdaYwG5PFAqk8odXLsQ5NcvBY8F3NH1Zs8LAhcaAbz+GaCXtG/Rj4YJ+63U4WwNzGOzzvvbfSGOC8FciarRqgGqwZG4UJ0przNqgPScsUWgetlLrEhIX8om8o8yW7mRfKNBvvyWKoL4eLax/E2532Knl+tKX6xoWxXLSePa6gHrpfJauYRNiNZzbxAfi4bJRw4kwNE3glk0VN1n01p3VxGXi1ZzYR2ciCBNfMcB2oxR8JBqXuJgVV6W8KKa0OxImSdNPyzqieq03GMh1ER8pp5mQ1lmlSOM91TtfNJEWsm6ivEDtUxCU+nKRQzFqv2ql6oTlKsCHhi4oGUAsUOcON10StCXjOvsBHpL+HezU3li1h3M41+Eg48xQHiuYS8elYn8peyWQPk+4deFnnNvM5GAtz78VupuVrdTJCakFkrIecZBzIYJCG/KwciHdiQYnWAvDzclpgZbERuSfVchZuJvzU2tx4rbkIcH1L9qIT/gljeSXiwGc7KPSghhj2bBx424nnk1ZGao4mNyHipnqvQA2iupAsxz27GNm6wBGVF9J46D/vGVW7swQOLf8fAxcJF9beMbhLycRHywBbH1+vBnO/ZlOxa7Lw8eVujM/YFSXidMkZGD09U44RUby8+SPWx1vThzjMslqKt6jN5jZKdnwIPEux9GfipJmNuvBZyDP4G8oZFn++9fSXU3Vwn9n22auxdd48FHcclxJriJybxjQSzVTfIM7DyajVnrIQ4dgr4fNQyXAiscBxrv4UaO7bIqHBTwur/IiEX79z43OqToueF2x1eRbHaH6qmV1JLSkpKSkr+MX8AcOgaUSkC4/cAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAWCAYAAABUpxX0AAAByElEQVR4Xu2VyytFURSHl1cMSEpGDEUpxVyEgYmBUkqRMEFEGUgpA4+JsQETM4mBkYFMFP4DkUfdPJNEySMpfstex11nncOdyJXOV1/3rt9eZ+/dPWefSxQR8f8Zhj02FO5gG8yDubAZ3vo6fpFF+ALfxF7/8CfeuLbQ15EkEm16Gs7COjOWVBJt+k/y05vugFNwReoyOA8bvQZQAufgpMo04/AELsBK34iQaNMHcBfuwFeY7usIMkHx5z8Gc2CK1KdwE1ZLL3+3PwzXfI1H6MHnpj4bCjyWqeo1yRJxRq4vS2VDknWqjOGs3NSaClN/wE39NvyCUnL9Y3bAEKPg4vxatRnDWY2p2VVYpXIf3DBgQyHN1Knk+vdMbjmi4Aa7QzKGs1pVF0imDcDhoA0pvrC+xdmSbaksjEMKLtYVkjF20/pxrKfwaz5Cft4sfHofTNZArr/V5JYYBRf77pfW/wH24DWZmvLJXTRjB0ARPDbZM3wyWRjXFNzgqGQZKvPuXIvKuC5W9Yj3ZZncxHzK+TXEn1fk/to17eQmOZfPbf9wKDcUn5fn5Ft8T24Ozi7hOtyHF5Lx2CNfDDbIHUJej12SPCIiIpm8AwpQh2BWUDSrAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAWCAYAAABUpxX0AAAB6ElEQVR4Xu2WMUhVYRTHT0RkoCIOLs3hECjpaiTaJASKUKtYg45uIgQO2ZKLgos2OLiIDQ7ioC4NgTQpiAY1PMwSURESoiXr/3/f+Z7Hc9/3mlSI+4M/7zu/79z3znvv3vueSE7O/0szcoz8QdaRuovbJV4iP5CfyHO3d6UMIJOmnpMwfItxZBtZNfUW8sHUVwoHZCq5WldH6FLfyqWyJ9mB/NAbro7QvfXyOhiRMEyXcf5NRFI+0oe8Rt5pfR+ZQZ7EBtCITCNjxllGkV1kVrKnbJFuCUNMOJ8aLuUjr+S8p4DUIDe0/oq8Rx5pL9f+uVjzmMiJWRcZRxaQ30in20sNl/KWePpVGTekrt84QtfkassDV5e4K6F5ybjUcClvKUi2Z7CMI3TtrmYWkYfGl8UP4+tIylu+SLbnRRlH6DpM3aDOpghPB14cltjQpvWp1h66HS8dnyV7LH+YvCN+6Ntm/Vj0mF5d+CeI7qbWT7X20LV66ShI9thKn7S9nvyF1xMXbLTviBcC3bJxhI6/npE36v7FoWT74m31lnHV6p4Zx/qeqYfjoh45k9BwpI9TcdNwR8LeR2QT+SXh9lUJ/p/h3YO3twMJXzFPtW/q9pEV5BPyXR33+N+GrEm4CPm6zLz6nJyc6+QvhqycZynzsuUAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAWCAYAAACosj4+AAABkklEQVR4Xu2UyytFURTGN0pGSJEMlYmUDJSJyMREBsJIGZhgKv+AiZEyZSymZlL+AAw8BlwDuXnnkcdAMvD4vvZap221XQY6SudXX3ev31rO2ffs4zqXkfF7VCEXyDtyhFR8bqdLqfObUYqc31hL4FLlwQrQhLxamRZ8GmPGNYv/E+6dv/la4PjU2oPawt4EModUIsXICDKLlAdz48gi0hk4pR5ZQfaQUWRdGyXOb0jDzfRo8wuGkC3n57uQefG94mqRvLhqcTNSE14/F9SNzpxInQgNd/0TOHsccfa4X4y7QZaCmiT9buRZ1h3SYHZ1oACcG464feMexSvTUvN1mXT+Pz3Bfhty4uLewpnBiNs07lZ8yKo4zTLlgBQx6NusNHCmL+I2jLsWr9QE6zJk20mfP36FNvQdnOmPOPuE+M6E1+OaGwlJ+lxMBQ3Cesc4Cy/Iv7W/YXSHxj2JV7jOB7W6BH3pDuRzIWxG4BO4RE6Rc+dvyOO/EneG3Mks3x/W9Dy6VufvoafDvCENMp+R8X/4AKDJeRftq0F4AAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFMAAAAWCAYAAAC8J6DfAAADH0lEQVR4Xu2XSehOURjGXxkTSmbhvxNWNiywkCJTKcNKCYmFkihSNthYKMNCGbKQRFhYKVMJC0PKLFnILGNkHt+n857/d+5zz/nu+VM27q+evvs+5733nvt+555zrkhNTU3Nf8FI1VbVnMBbGxz/FS2qX2xGeKeaxWYTDom77i1VV2rzLFQ9VX1XbaS2GC/FXdPrm+pF0L6L2vm5EK9TdVYtsHin6naQ89p8Lzz3K9UHi3+oprdmE7GbMkvE5eQUs6O43CEWt7d4QGuG47DqSRDvE/cgOVT1+aaqL3lfxI1IBtcJiwn6mH+BfDBKEvc+Lo2KNwP/fm4xz6oekbdJyvdA3CHiTSYvRlUx0QcG+cPYVGZLuphnyPeMZ2OQ6qg0Xp0Ub+03t5jI207eGPM9Wyj2wLvHZoQ/LeZ+No1UMU+Tn8R3plkx56nm23FOMf0rzRN6i/kzLf5qMVNVJE9VXqqY0GZuiOCLeZIbYhxRDbbjZsXE5OvJKSZWSuStIN93brXFqWKkfKYq7xwbykRpnOd1R9wAYHx/T3AD00uKwzdVzOeqdkGcU8wJ4vKWkd/TfKy2IFWMlM9U5Z1nw8AA8m9FqH5hkrShmNyJWDGnSrkgOcUcKi5vOfm9zd9gcaoYKZ+pyrvIRoQeqlMSv1ZWMXdIeUWLFfMTxSCnmBjJyFtDPkYE/LkWY1/J9wSxB4tRlXeDDWUKG8Z1KV8rq5jHxE3OoXzHcLzb8jjnsuVg1YtN7iHIS63mfq+JTvIDAHg/2YxQVUxs5pn7bBijpXytNi1AIVUdA/715ZHZRbWUPHwhXCNvlRTv0Z9iD7yVbEbAFge5scUDb8d7NiV+P7BIym1VWyPsz6PkFHOsuJzF5PtzRwTeOPNCEG8jDyPwQBBPk/J5zcBC8pFNcX6syLg2Pgu5DT5PS8PN57l3oLgpsNTPK6pnqocmHF8qZDjeqB6Ly8GXDWLPDImf40fiQXEPt6fY3Ara7kpjuulWbK5kr7jz8DbgFw/aqZDR4Kqqu+qzuFxs+/C7PkwyLxTmd3yKYrQ/UE1qpNbU1NTU1PxjfgNoQiKLMtAZmQAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAWCAYAAACosj4+AAABjklEQVR4Xu2UvyuFURjHD0omWcisRDaDUV1mGYRJGSyY/MggyoBMSjYWKZHNJv8Bd2DCom5C8jsDZfDj+73nOa/nPZ1ubulVej/16b7P93nuec99f1xjUlJ+h1G4DZukboQbcCSaSJg5+Ol5FJtImBm4DNfhNCyLt5OHm2jzw79kyhS/oVY4DldgFSyFA3AJVqq5YbgJMypz1MFdeAwH4b5rTMJ5Y5+dNfnkiQrRBw+NnW2Hq5J3SlYLc5JVS7YoNemAp6rmC8WZPGNw77uXh81ZLwvBufNAFi0uvHnZHdxSNfG/EyO0aAjO9AeyEy97ltyxIPUTnIDlqmdKdCG8m59vqDeQZb3sXnIN74r74XTHNVg8uEJl/gIhONMVyA687FZyR406rjD2fy/q84CXTVPMhroDmX+F+Mzo9XjMjWii/quxb4IjY2yzQWUhuCDnhryc2ZmXvUju4HFO1S6L4C1zV4XyP6IQvALX8AJeGXvCHngj2SV8lFk+P6yZ89a1GHuOZvmkH7Be5lNS/g9fJR90ckFHV78AAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAWCAYAAABUpxX0AAABz0lEQVR4Xu2WTyhEURTGDxILdmJhLQtS7GVCWVFKyU7YIKIkWVlgZWvDRjbyZ2EjkY21LJViMfkbkoWipDjf3HvNmXPve8uZ0vvV17zznfPuPTPv3XuHKCHh/zPDGtWm4Jj1w3pjDalcXtlifZFpBhrLTf+BXKm9HrDxczZdOKKaPmTtK++ATH2P8vNOVNPfZHJ9wmuw3pPwCkJU07WsTeWlyNSfK18yyFpm7dkYX3Sd1e0KmHrWGmtJeJIF1g1rg9WSk7FENR3iiEx9o04IFim7VtKsSlaRjW9Zp6w2W4tr+BLEuMeBDcADRePaDFBCpvZMJwLckaktF9609fQOBK9JxZJmFWdA0YQ2A3xS/GshSZM/ObZV7QF4KRVD2ARahZ8DCia1qbhg7WgzhmvyGxwJeABeu4irrSflAXNKmwIsKL1g8G7GcUX+ZMMBD+imy8R1J4XvyZh430LMkn9a1rBWladJkz9Z3C/dIWK98HpVTFVkblrRCTID6cfk1CXqQryQ3+C89dwJCyqs1y88xHUinnMXu2QGxirHo8YnDgwc7Q7dqFSxqNO8UnZcjIlH/M66t94jmf8zl6wH6yH3gZuZEzKL0M21bf2EhIRC8gsXwotraLXTuAAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFMAAAAWCAYAAAC8J6DfAAADEElEQVR4Xu2XS6hPURTGl7yFyFu4M2GkxEAGUkSUEiZGHgOlJIoUA0wU5TFQHhlIIgyMlFcJA5S8SQZCKI8BeT/X1177nnW+/97OvfwzcX71dc/61j7rv8+6+5x9jkhNTU3Nf8FY1Q7VPOetc8d/RYvqJ5vGetVb1QfVYspVcVRC3buqHpSLLFI9V31TbaZcilcSakZ9Vb10+b2U5+tCvEHVVbXQ4j2qe27MG/OjcP2vVe8t/q6a1TqaSP0oQBNOu/i26pKLc3SWUG+ExR0tHtI6InBM9czFByVcSFvIzTlyRzWQvM8SViSDOr6ZYID5l8kH4yXz26ek6Lind8ID8PqwSVxQPSVvqzTWQ9wp4U0nL0VVMzEHBuNHsanMlXwzz5MfmczGMNUJKW4dz/WEB+DtY5PAmF3kTTQ/sp3iCLyHbCb402YeYtPINfMc+VniZFLNzE0250fiLc0P9Bbz51j8xWKmqn6kalyumdA2TiSIzTzDiRTHVcPtuJnNxE6J/Ery4+TWWJyrk/OZqnEX2VCmSnFe1H0JC4CJ8/V7RpJ+Ul6+zWzmFAn55eT3NR+7LcjVyflM1bjcRokFFO8Kr0F+kLSjmTyJZjZzpIT8CvL7m7/J4lydnM9UjbvCRgJssmclXatNzdwtjTtaM5vZQUJ+LflYEfAXWIz3ylSdqvqRqnF4jWNmsGHcksZabWrmSQkPZ684MRzHnfqdeQw83vkYjMnt5vFdE5PM1f/BZoKqZuJlnnnEhjFBGmu1awPypCY2P+EBeONc3E21zMUAXwg3yVst5XqDKY7AW8VmArziYGxq88DdgcXApH4PLJHGXNWrEd7Pk6SaCeAtdfEW8zzx3DHOm2SeB/FO8rACD7t4pjSe9zuwkeAzl4GfajJq47OQc/D5sTTafH72DlV9tFyJa6oXqicmHF91+e5SFLyh+iThv+6ZLeVzInElHpFwcfvL6VaQeyDF46ZnOV3JAQnn4W7AX1xol9KIAlxDLwnXgbH45sbfjX6QeV54vuNTFKv9sWpaMbSmpqampuYf8ws9hC5YeW0HVgAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAWCAYAAACosj4+AAABbUlEQVR4Xu2TzSsFURiHTxaykg1ZSmywsbBRStaykM8iCxY+lvI3WClbdjYsbOzkL/BRyMJVUjch+YgsLJTw+5n36PXeM9Od0r2leerJnGdec6aZuc5lZPwNJ3APzsFxOApH4LBYcj4TfFZzJYMbd8FW2AQbRfaycGgD2IVtNpaLTrhpo4FPdB6uwBpYASfhMqxWc7NwHXar5uFb2IancNpF33GQYl7VGDxy0WwPXJXeJ60e5qXVSluSNemFZ2rd4mL2XROLhRe5DDR78TfTHuCGWhP7P98wNtiYAOcnAi1n2ot0z6Ks+StegJXq3A9TLuYuE+D8UKAdmPYoXbMjzbv1+7Rz53IiDZzvD7R90+6le+rUcRU8doG9/Z2mgfMDgWafEL8ZfW0e80Y0BXunvSFekPMzprNdmPYq3cPjvFr7VhDebYyBT+AWXsEbF204CO+kXcMnmeX3wzU7X12Hi/Zql7/0AzbLfEbG/+ELy5Bt8uXVH94AAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH0AAAAZCAYAAAAc5SFpAAAEsUlEQVR4Xu2ZaaiWRRTHTzsVZdSHyiixPljYRgsZVNKmSNJuH9pEoQ0iLApaqA9FmIWG9SFCDGxBKoIiCAqK+thGFkV7QtG+kGGbZnn+zjm+5/7fmXmee6Eb3OYHh/vO/5xZnmWeOTNXpNFoNBpj4yAWGuPHtmqL1K5X28O0aQP3v8JhalexGNhNbbHaA2pHBH3/8Hvc2FXtBbV/1F5X22aku8rJah9IqvsY+SLPSIp5X2178jGz1dZJinf7RW1BiPmd/Ih3HlbboDbd7Em1Dy3O+UrtT9Ng+P2TjOz3ua3R/fiaBWOyDNq8V+0otflW3tn+Rr5X+9t02Hq1H9V+VttkGl6cMbOfDDoHe1kZM6WL6yQNzrlShi8AswzawVbe18o7bo0og1mD2KXsCHB/foMZv8mM39gc30jy7cCOAngxmQsltfEoO4xa/yXfXEn6J+zoy69qj5P2htofpOVAx4dktLuozAN/V9Ib24U/9LvZEeC2X8xoTk7PjS/S5XcWqp1KGr6YqItZWgI5QKn9Wt81XyeoeAFpN5te42zJx/gn08Hvj0IZYObm6jL+0ONLxHA772Q05z0WpPvmnSXJfys7iPjFc3ypOIAdRKn/2thqvionSap4AunzTd+T9MhLku90rQz0KfZ7zcC9hdtM909+CX/od7IjwGO4wrQ+7YM+N69PzNssSL96APlFjlJ9XyK/Y0cfkN2iMhKLyDzTjyM9gqQiNyDMpqjjN8/0VaafRzrjD3A0Dx1gafIb5lbKqks3NtIVc5+kXCLiuVGtXhdeH0sADEsp7gW0h0LcqLhdUgOHk36O6ReRHildEN74qOM3r9+emd5AOnOZpDhsc0rkxgBWyGCMbh+PiEiUriPSFZPzTZXuel14/VPMZqmdKWnn8rn0S7aHuFxSo0eSfr7pnJhE8EnKXRCStKj77mAfK2Mpedm0E00rgS0a4u5hRyA3BuYMGdxAvtY+D6YWM0ntERaNWr3T1Y5XO1ZthqStL7aXkVp99/muqze+pqPzyCWm44GVKK3pn8qwji0P9spfSnoA+DQhpmu/frGkuPvZEeC+rqWyg1mB2OdJr91YsIskP/bKOV5R245Fo9b21Wq3yCBmpQw/h1p9n7A4fxgVO0mqOJbs3QfMcPae41XpjgHIehH3FDsC2HJGaskN2noto9XG8qAk/9HsMGp1l0jyd720pTZqvjlS91dBJSQiEZxEcWNI7vYmDTGc4UN7NpQ/My2C8nLSStQu7A61maThNGsZaQ7auTGjldrHlwi+0iHIMdKdl/gJWola/zXfWslfTy9ysxrlc0PZDxk4DidW6NzBuo2YeILlx6WOz5y+eEJ0E+mnqX1BGsBDRzw+f5FrTGdy1wWQR0DHMlbiWxYK+G7iUNL9fuX6ByXfE5L0vv1nWS3pjcRfNIatHPO0pH9eMD9I6ty/DgeOdMvupiMOfWDmjxYc2eJUC+34VrGUPOGhY9lCxu83DcYnjDibj37sKDaq/SbpDB5rbFfOUVrnc/j2GIZ+8BdJL8CxaiSOK44NEwjX/6YMr/+NceBSSRl443/EXyw0Jj5vsdCY2OCfL7yTaUxwZrLQaDQajcZ/yGbaTJ4FwFkDjAAAAABJRU5ErkJggg==>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKoAAAAZCAYAAAChKLVZAAAGKUlEQVR4Xu2aB4gkRRSGnzmjGDChYIBTzDl7ZzzELAYwrTmAmFAwIGJOGFBEjHAGxASCKCgqBlRMGFBRDDfGM2PO6f1WvZs3/1RV9+56OMPWBz87/b/q6u7q6upX1StSqVQqlcogsxIbA8A8bFQGh9lVx6tOUi0SvUnd8CxhDdXRbDoWUl2guka1lvOXc79nBZ+xMawsoHpI9bfqedVsveEiW6nelLDvbRQD66geVq0rofOsqLpCda8vRExVfSuhTtN3qoNdmZ8pjvLGzarfVKtF3aV6K5YzPlH9Gj0Iv7+W3uM+MLN0O2awEVlGunVeLqEtRuL2fPGv5wvVX9GHflB9pfpG9Wf00Nnbgn2HnmWl22BgsbiNTtXEiRIa1DhK+ht92+h5fd5TIg9GJ5S/lAMOPp51CsY6BmPnlOJTCbG5OJABDxOzr4Q6buVApHT8XGwnCf47HEhwhGpzNoeRH1V3kPeC6hfyUqCxVk14F7rtyar7VTeozlYt6GJNWEe9mAMOvpGPJDwj5ec6g9EUNw5RbUMe3kzYtzSiIafN1V86dinmaVNmKMCF7E3eadEvsZuky9jr1MDTfJbbHg3WUX3HZ/gcXk14xutsSPMN31VC/AwOEP7NYlgasTwHiNzxS+dWinmeY2MY2VLCxfKrYST6i5LveVTSDTVdev3NZPwd9TwOOPgcjowetArFUrS54W3KvMKGtNsPIF9Okdt/aQl+UwqFPHYJ8g5Sna+6O24jh79etbMVkDDpvE7K7Y5JKs77ag4oW6ieUj0rYRB8uzc8ejArxgUjuffsFf2NyPcgsU81IkYt728iYZIF73bVT6onXLyEdbpSg6XOAWmL3WRTbjae6wyepjJXSsiNPZbrl/ZrwvZHegAhzUJbwLvJlcuROva50q23I2ElwlKUD1WPS0jXAH5zHVjqgndA3N40blsef4n05uOWo48L5IyoZE3yd4/+fuR7cjcBI4v38RC877YB4k+Sl+JwCWWxpJMjdQ4Ao4Sdoyn1ZOeuw9NUJhVbQZr3a8L23zpqe9UuElY8PpDyhBdvwxvZjHwkod55nXdC9JBre+D5/oGBBvMazx8SVioAymOA8YynDf4FM0JUsjb5e0afJwceDPupE3hN0r7HZtNNYDkK5fCU5mhTz47Svel8reaXKJVZWHULm5HSfttJeNtsoNpYwjIfXsOe0v4Ws9Ua5mnJLzN2pL9eS7MYeFNoe5pqSacHow+eib870t9hx4zlqGgwD4Z1+Fi6ypHLUd+VtO95TEIZXGSJ/SWUu4oDDj4WRoYUGH1QFo3qsRueY34JcaxlpsDrcQ42I6W6j1GdLt0yGP34PpT2t0EG68MpcvsBLGtx/LCEB+BhNAcrx2282rHsyDKsftOZLjYmLN8Yy6zfGpnhWX+qsbH8Bc+/elJgtoxy93DAwa+h0gQDdfEsOHV+nmslxNfjQKS070US4k0PWq6OUmwHyceRNx7HpgMpEO93aMID8Kyj2nZuTRhgomcg/cD9SNU7alAJJgMefJHhyjHB4hEQZXhlAN59tI0vQx58NeL6c+RuBjhHuom/gVzpMvIM1HNKwsvVP6eEWG5hfX3VyWwS9iUpR+n4pdh0SV8PwBe2Eh3pr7c0ovoUENu4JqYT/+bqyL11WpMaPbG9h9u2WSGXQ66JBjOWklDGf8l5WcISlWFLKyPOK2GTklPJx6sGs1QGHRXl8Wr0HBt9JnVdAHkxfKQ4Odp+Q7dViNXJt/ZKHR/kYndK8HPH95+TU1gbeawf+HuHjzPw9nEeBit4fm17qoQ3LEAslV79J2DZCE8J/qJSLFsx+DaPtTPmSwkNZqMwvuUzb0iI2Ujq85k2zC3h6w72tWWx3AQGNwEpDVYK7EZD/KXNzsWEBfvfJcxqMSIhZ8SIWiKXt6awpUAIx8FfTDwBPol6/Hn5c8NsH9f/ovTnswYe0ClsOtCOmPXjIcd9w734XvVx9GZI+L8P/P8GJszwEEO7GLgf70n3/Py8ANuYKFoMqZn9U1Dlf+BACTdk0Eh9IatMYLB2OIjwZLEywXmJjQEAefXibFYmLvgHFV4BGQSQE1YqM5nMxoCwIRuVSqVSqVQqQ8Y/YDcOGs+DGfoAAAAASUVORK5CYII=>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAZCAYAAACCXybJAAACbUlEQVR4Xu2WOWhVQRSGj6KohRJUbILGws4mINgoWChikcoiNunSRMUNBCtttBDUQnEpYgg2WkTE2AS3RhEXEFRECzuXQsR9X1DP78zIuf+dMz4RUzzuBz9vzjcz9868u3BFGhoa2p2tmrUsDds1bzQfNP3U9zfs03zRPNcspb7EAs11zQ/NBeqzHJUw5qFmHvW5nJCwAExE1lW7f3NPc97UdzVXTN0qrzW7TP1Rs9vUYJmEtSS6qU5816w0NcasMnVLeJueIfmTwnWwLLBc6seZmXGo+Y7Dhblm6p1Sn9eTcX/E2/QtyR8MDrdXq6Q7ioHri+05scav5Vz0CbRx9zHwc1mW8DYN7y025z0w9itLCf5ObO+INTMs9U3nnnX4AyxLjMem8SJk4PFsg9OxZg5JfdNnTJ2AH2NZAhPWsxR/c573wNgXLKV6nEumbdkvwXdqJsb2qcqIAPwDliUwYQNL8TfneQ+MfcVSgsebGByPNXNQgp8Ua7RxVzDwl1mWwISNLMXfnOc9MPYzSwk+XR3vmR6Sqkf7rKkT8IMsS2DCZpbKW8kvBO4+ywLenwR3JLaXxPpf3t5rWJbAhC0slV7xF7vI1NM0m0zNHJb6cSZEN9k41KtNDd5J9X2ADfOxFmdckdkSJuzljgj6Bky9JzoLagQn90D/QlPfkPobHVf1m6nTHzPfuPRRM9U43JE3Te0yonmmeax5FH+fSviQsOAq4iRY5G3NJwmLseDqPNEcI2/pknCcixK+lzE+B87xXnNSwvgV1e5fwKFvVPNSc7XaPX5M12xj2e6UrnJbMkvyn4ZtzRQWDQ0NDf+TnygRyC80mHyLAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAZCAYAAABzVH1EAAACUElEQVR4Xu2WT0hVQRTGT5lEuKts48KIwiiIcBNSZGKblkm5sWgXuLOgRX9IsAI3LZRKWoQEkQgtchMUtWmlFkRt24TQ0qjQ/phW5+ucmXvucZ5ec/Xk/uDjzfnOmbnz5s3MfUQlJSVFOMcaZe3ReDfrAasnVhSnjvWM9Yf1irUun47cZM2xplmHXC6wkzVBMtZzl0tynaTY6k2uohgNJH03abxF4/WxQvhC8szAd1a/iUErSd/Afhcn6WUNsu6zrrBq8unCzJL8spbXrB8mbqfFE9qc8BB3Ow+/4LjzcmDybd78D/DwTuddUj+AyfhJA3intL1NY3xawpatyGVa/Rc5TPIQv9/PqI9VB2j/ytIR+O+0fVVjzzCl/chF1g2SolB8N1exPLgY0K/Z+SfVP6Ax2l+zdAQ+zgp4rLHnNqX9yHnWU+ehwzXnLUUfSZ99zj+ufpfGaH/K0hH4YZIvTdsyQOLjUimMHbgIZ0nqcbtYTqiPQw7Q/pylI/B/a/uhxp5bJP4Gnwik7voFSg9WiXBGWpx/Wv2wimj/zNIR+O+1XemM3KO0H0ESLybvLdnJsZGkfrlbq9K48Ia0fVDjFd9aSF5IeL7TMdZe51lQj/eR5Yn6gTsuBtgR8GqNh7jDxGCG0ucr8o1Vb+IjJAM1GS88zE/C4lcfpCYEzy7IJC2+ybD68yYOz99uvCTYWmGi0I58+h9jrA/edIyQnC98YpzU/7VGktwL1hTrYz4deUvyb+ERSf3RfHp1YPXWBH7rVCXYt1u9WY3s8kZJSUl18Be3lqVxYDINfQAAAABJRU5ErkJggg==>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAZCAYAAABjNDOYAAACgElEQVR4Xu2Yy6tPURTHv0QxkYSUSDIxopSJgZRkYCAD/gAGHhEyExMTxYQYISMMSB5FHhmQPEpRXiUp5BEhr5CwvvY6t3XWXfv8NgaU/anVXeuz9l6/32/fc8/5dYFKpVL5u6yTWOalYYPEW4mPEotdr2GSxBWJ7xJnXe9XKJ2zG2nNQ4nxrtcwS+Iu0rp9rtfJAYkvSBsZy9vtPm5LnDH1TYmLpiYzkWY0THV1KaVzvknMMTXXzDU1WYu0rmEp4lk9yR3OMMQD6Ya72l95PPjLzvWiZM4m9H9P8wLHenLgNjvXk9zhXEf/FyV0vKzJaK3503JafSmlc5jzavbQj9N8vtaez4h9J7nDoY+GWb/R5Ja9iH2O0jnMo3sR/XbNz2nteYDYd/Inh3PE5JadiH2O0jnMj5m6gf6k5m+09txC7DvhhhVeouxwzpvcsg3Jj/WNDCVzBmp+uLUiQX/P5NGsG4h9J9yw0kvkX8T6/Sa37EDyg3wjQ+kc5rzKPPQXNH+itYdP2sh3wg2rvETZ4eTuFXsQ+xylc5ifMnUD/S7Nc/ec+4h9J9yw2kvhHeJhdHc0n6F1r6dML0rnMM89rRZpvl5rz28/rdZ4KSxEPIxumqsXmJq8l3jl3BKJUc5ZSubwYPx7mh441iMCd9y5TkYibdrqGwp7/HbZsEWdhb/dr6YegLRmgnFT1Pm9lpI5/MB0Q4zjFX7N1OQZ0qO7YQzSvsHGZTko8ULiscQj/fkc6RupZSjS0KtId/tPSG/aw94HiUNI62e32z/hDL5mFyVz6Ng7KvFa4lK73cdLpM90Amn9xHb738NeGRVH812k4niK+E+ygvz/XSqVSuW/5Ae4SfBgPUsISgAAAABJRU5ErkJggg==>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAZCAYAAAB3oa15AAACN0lEQVR4Xu2WzUsVURjG38BFKX2gIkItCtxUIH4QES4KCtpGQf+AGzMMBQU3udKVEQS5qhCEalFQu6CCICj6ACnUorVBRmJQGSp+PQ/nzPWdd+bcOxclAucHD/c8z3vOmTlz5xxGJGd7cwQ6YENDvQ3+F2ahQeg6NGVqEYegNRuWohe6ZEPFVegX9BdqN7WIBuituIs/NzVyAVpR/ge0BL2EzkLnoJ/ixteofkHui5uAA6jOeLnAJ+iZ8pPQK+XJSYk/tSbjyQz0Xvk+aLdvV0IV0FHoXqFHGYQWsEeSN0KY7TPe/oN8OG+UZ58Xyp+CTitP0q6VidACPkj6pMxu+3ad9/zVPPV5xBOJv/dD0E7lxyXjq5NGaAHMQwuI8gHV1oxKPD9uvG7zlburfNlsZgGPVVszIsn8hriNygOhUeW2X9lwgss2lGwL4CmS1oc3y3y/LRgmoGrlR8Xtn2aVlYQX6rKhZFsAT420PjfF5TxdQhyDxpT/BvX79jS0Q9WKwgtdsaFkW0BoD9yR9Fyj67xZ2/+R8UE4sNuG4LckJyXMPvt2m/elTiELx+9V/oQk+88bH4QDe2wILkpyUsKs1fjzypM/0JzJInizt0x2WJLXyrSAWnEDr9mCh7UO5Yd9puHTXlY+eh0OqkyzagOPnbfoK/RA3PfIV3Ebhr/fxZ0Aml3iJn4HfYQWJH1zscYn9lBc/zPxcoEvUJUNPa9l4zgvaxP/S/g1Wgw+9UWoxRZycnJycraEdYbInw1tbm9bAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGEAAAAZCAYAAAAhd0APAAADuklEQVR4Xu2YSehPURTHjzELQySUMUOIBRbKUBRhIQspiZUFGf6Gkg1JoSwoZFiYSiJDQiFigYUpC0JJ6W8s8zyP5/u79/x+55133++9X/Jf3U+d3jvfc17vvnfuu8MjikQikUgkmyVsc6yoOMP2h+0N20wTE/qyfSCXd52tSTJcZj3bd7ZXbCNNrCHZSa6t39hmmJjQm+0KubyzJqbZQS7nIVs3E6vKfnIvAxfD5ibDZRBr5s+nef95JVwCN76k/Fbk8tooDbxjW638L2xrld9QPGHrqfwjbLeUD0aRewZhkPGF32zjlI+cCcovTFYRTrEdNdoJcvmTlBZq3Hy2u8ofQ+m8dgHtfzOE7YAVKd0O+HZ0QKe9rPxVlL5uYkArRFYRfpKLTVHaAK89Uxr8wcoHC9nqlS9fnQVa1nAgNGZra0XDLCtksIHtqxUp2bYO3sdRI8OygPM7yhegd7ViHllF6My2x2ijyeVj3BfgwzYbrbXxfyhfgH7TigE+snW0ogfDC8bvIgwnd89f5IZNMJ3tdTmDaAWFO8xuShchNFdA32TFPLKKEOI0ufyBSsPLkULIA/ZRcQD9vdEAdMwNRfhMrmNonrL1M1oe96jS1vPe12AIDhVhC6WLcFz5AnQM5TWBi+ZZMQBWPMi9ZgPMMEoW4lgyXNJ0bxMkvyi6EChAfxWrhU+UbC/mJ+GC1ywbyem4P4ZInGNSt0C3hc0FF9VZMQB6rB6GhOVsD/z5bKo82K5yhvPfKl+AjhVGLaAQKID+GmsB98Tc1ojcis12hH3GFzDcQm/qfZzbhQuAftGKeeCiBVY03GY7aEWqfB0WvCit4xxrcgv0WnsNvigUtKY1uaeebY3RpONguAFZc4LsLQScY3i2QN9uxTxw0SIrKg5TuuGP/BENl3OLbXDowaBts2IVUACZA1CILipWhFAbwDmqzE0jyOX9y+poqhXzwEWLrehZSun1MiZi6TW4LuvBtL7V+ADDATTZDOahCyCgEHayrgbu196KzF5yO18BeZOVD7BC0/MaCmCfaWhAywUNwkXrbIAqG6yQjVd58PWuEZykdA9HHsZi4SqFV0whXrL1sqIHv1M6WTEDdAbsfzQtKf3i0Ot1nnSYHkqTzWYLpeHXTWjeDHKI7QXbY3LDCY7YgGFTJdgXrw2rAwGNwLIU+n1/XKbiQndyMXz6+M+C9X0RmlP+sLPSClXA/yu0A8+PIzZvoa/xBrlVFIZj5I1NhktAQwyrQXQG/fsmEolEIpFIJBKJRArzF2ejIkMecRCCAAAAAElFTkSuQmCC>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAAB50lEQVR4Xu2WO0gdQRSGj2AwhakCVhpByQMEQXsxqK2IKCSQJmgasRArg5WiCSnEUnwVtoKCVqKEQEiXQOqAFpfEJyoGQqwE/Q8z4z2eGWdvIbLFfPDBnv/M7t2jO3svUSKRuAtq4aUOyWQTsA++ga/hK2uNWJcr+Kb1ME9EHpL7uWML/id/mEE4DZvgM1gP6+AInBPrckM1XIcn5A+zqWqmHJ7rMC+4AULDhLjQQYC38CNcsXUDXICdbgF4DufhB5FJxuBvuASbYa9shlil4iYuZZgZOK7DAJNU3FcF+AiW2foP/Apb7Vo+1p/LNZ/jOIMDovZ4DL+IupRhsvqSXTLrH4ps2Gb8ZpRw1qhqCe/Z6DD6hKxhpije1xTIX883pDOGs5eqZtdgi8iD8JvohcqyhuHedx1G2CH/eu8CGcNZm6irbCatFP0bbMBvSncSHy8Wl17DvU86jLBN/o33BzJGD1MhjjvI9P+KLBM3TIguMr0h3YhQIP96sf9Mu6h5w0u6KXzercSGmSXT0xs3xjH51xu12QOR8ePDGf88cnD9VNTvyTwxmfyEh2RemSwf/7ixgqiHzAfw+74UTsm8zfh6R2QelX9wz2YHZH51/IL7NuOe+zL+TGbzuz/wss0TiUQikbhXrgCRuI++7pt08gAAAABJRU5ErkJggg==>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAACBUlEQVR4Xu2WP0iVURjGX4VQK4cGXRoyQRxEoRYHi6RcHYLQVdTFsUWkQYqyoVVyyEVoChyao0VbHJycBBsu/pf8F4pCg/Y+nHPufe77Ha/l4L3D+cGD93nOew7v8X7nfFckkUhclUeqXdW5akFVXTycZ1T1R1zdEzNWEUyqpsifiGu2mTJwrFokv6/6QL4iQOOdkQwKfDQeNESysnJLso0Dm1kfQDZmw3LyVtVlMtu89QFk2zYkBlTvVbPet6mmVb2hQGlVfVJNUMa8Vq2qZlQPVS948F9Ak2fGX7SZWB54J4WanKpeVeX9mmpOChcJPtu14DEncKAaIX8pS+IWuUnZG58xfT6zuWVdXE0tZS99NkgZQNZhPPNA/mMzuAiwAA63BbfZPPkdcbW4qkuRk2xTaMhmAFm38dBX1WPKL+WOuIk1doAYV/0Wd50D1PMGY/yUbOPDkQwge0q+0Wes2zQeBS9Ju/hn4y114ubgAJdiRbJrD0UyYDfD/9geceOHlEXhwx7g7J64hfh9hK8+1pAlJ9m6Ut/MM/I48Mxzic/LE36exBTA1Q3f7j1uGPj7+YqL+SXZBl757AZleHyQ9VMG30Ie77Qf5Iu4K9kNBJ1SHQgHfsP/bSoajbMn7jbDNYz5eFSOxK2BbEv1TbWs2vQZxvCTCnyXwhMAffF5IpFIJBLXyl8NCp+yDzmVOAAAAABJRU5ErkJggg==>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAZCAYAAACLtIazAAAB90lEQVR4Xu2WzUsVURjGX0FduBJRXEjQzv9ApIWbFoHgTo1I4RqCpRSFBQlCoC1auLT20UJBkBbt2pRuRIhIXIk7i4hA+iRNwZ6Hc8b7zuu5c2dajXB+8OPO+5x35p4zdz6uSCQSKTv34S0bZvANzsMLsBH2wnepjpKwBP/CE+9kejiTZB/tvVRHCfmfRc7A53DCjJWWoos8tsF5oOgij2yQg6twFr7wdSt8BO+cdog0wTn41I9brsEt+Br2wc30cDZFF3kobiLf4bK4/S+lOs7yEB6I630CL/ucE2bWDxd9NugzPtgSNuC4qp/BL6quCw84ZcMMfsArqu4Rd4w2lYXgJNlnn+TMdgPZqqm7VU0KL/K2DQvCY3DxWVTE9VmYDQeyN6r+7bP34i7bwnBnfW/Ug/eOhccILUAzIuEeZrxcbbZmsp8+TxxID2fDHe7asAaj4vofmDzPIq9LuCfPIjvU9kWpvuNzw+ZaL/Mh2KnqG+L6u1RGmO2YzFKR8MRqLXLd1JZQFqRdXPOCHQANEv6FbP0qkIWYFtfXrLIWn42pjDDbNvVjVfMVU/c7V+BX+BHu+U8+rXgZaF6K+2+rSU4MXyH8/CPuhGTxC34S912f4Vv4wW8z4xgfLrwdOI9kTvvcWdzr56ZUTzrH+L85EolEIpFIQf4BqXyPiRmxjDAAAAAASUVORK5CYII=>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJcAAAAZCAYAAAA8JbzRAAAFSUlEQVR4Xu2ZaaitUxjHH/MsMpXxhswiUz5IyJAp1+yLDyIyZMiUUMdQUgofKFMiFBJJkukkZCplFurcDMk8z+P6WWvd/ez/WWu/73bvqXvuXb962nv9n/Wu/b5reN5nrW3WaDQajcZMsI0KjcWTHYNdH+xop13ivs8E/6jQMJuw2DF/2XgDsHGweRavfSPY6kPeyO/Bzg62XrCVgu1r8ZpRfGmxzWx/BPvC+W8Rvw4q5cuCrRDshFS+Odg7rs7XSc/2fbCvgv2UyvTFIfNrd0PUOlfFJZ2ngu3jyhcH+86VaxwZ7AVXnrI4KIc5DXQSYHsP1ahTmjiet4KtK9pvFiOWQjt+csE6SX9JdNjVou8edVT4WIUlnaWDfaaixU7dQEWBOv6VkzWdDJQngt0a7NhhVyel9jzPqmCx/lYqBo6y+uR6RvTMXhb9umBK/KzCbGXrYBupWGApFYS5Vh48tDkqCqWB59WFxv1ltM44lH7DU5tctWhTm1xPi+7pugc4PthBKs425lh80L8trhS+n+wrOMhvdlFRWMUGnbdZ0sgdujoTTg12nGi8krjW51592qrRNbC1yYVdq44CeXI9qQ7H+xbrjFrM5GeetS32D/fAJxwQ7O5g2+ZKgcOD3RfsTKd5lg92m8XX/8Sw6z/OCvZBsAcsbmCuG3aPB5NKmbSY8G4o+i9SrvGgDQbk1WA/DrvHojQZKD8R7JNgj6YyyX0fSu15nlMhsJ8Nrsv2brBlfKVEnlzcX42HLNa5Qx0OjYib2mDTwUbiw6Qz6dDOtzhmLG5SE7RvU50MeSn6mql8fypnvgm2nSuTN97rymNzoAqJtSyuHt+hewzVGM2bNnzt9sPuXtxg8dotRUfbxJUvSFof8v3UeF6FBFGGXap/JkwndZ/JxeSgzqQ6EtfY8PN5SvfPZgmNqJS5KGkeylcWtBzl+L6y88ECTa4+LKtCB2y9c2L+ng06ZNX5NbphcnPNbuqoQF12qV2UBsfzsgoFeEXzW6W2+kyuxyzWuUodCW3Tg29KNDZQes05ojEelFnkLIhsaDkVyM8zGezgpC0wV9ugYULlKPZUQbjLpr9aiHi0zXu+D2waqF/LSZZTwcoDXaKrHhFXqUV3zuG0rT6Ti9cXdXykybAAR0ULrntbNI4s9D7OEI1xoUyexrmgt51SHfqVNCn3EbZF8v0vXgx2hSvfZLHRI5yWudDKHeLh2pzIey616R1Qg3rkDpkTbdAmySh+zow8aAxaF7nTapTamKdCgqiqbfVJ6PH/qWLicRv9puDa10X7KOme00Q7JZU3d5riN007WHdfdcL7vUReledZPJNhRZPEdsE1nP8oJ1nchWRWDHa6K2d+temd6yPenRZzQX8ksprF3yWX6YIjBeqWknHa/EFFq3cwz6S+rqMIJg9+dt4ltD0Fv0bXUuSib1WjfKNo8Ej61PocJqs2FqMiETP5dothmI7swzFWviE0/1uUMf/HLDugrKtl2AnprnXKyr9Zg8S8dECJXpp0tM3fOOpDJ3H2cB6Hrrnb+hbvGx/5ZAnyIf7NGAXXE6k87Ar1+S9Pmr9n3jxoc5zGIlgjfcd3qPPtbvEvrUWK/N8bRxCEf76zZfYQDV8RzU8mNQ9nbWg5kdXO7gMRkGvzjpiBry201yxGR6IqdfnPkE8G0KP3zLNzTkc0ZOHsP6hahAhUg0HneXlW6jHZgU/K6J9bzG/5PY5p0D4N9nCqCzvb4OwQ82dk3CNvsuzTBdKYxWhEbjQWCqQTs/7vnsaiCa+qRmNG0OOFRmOhwdFMo9FoNBqNxY9/AUqqomzxHeZPAAAAAElFTkSuQmCC>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJcAAAAZCAYAAAA8JbzRAAAFLElEQVR4Xu2ZaaitUxjHH+M152YW7k2SMTIlJGTmJu7liwiJDJmHxAdToZThg0KIkLF0ux9kOgll+mIWioyZp8zj+lnrOXvt/17vcM5x5JzWr572Xv/1vO9ee73PWutZ6zWrVCqVSmU62EKFyuxk22DXBTs80y7Kvk8Hf6lQGea7YAtVbOF+i536erCVpM45LtgnwX4PdqXUlfjC4j3dfgv2eVZ/s9TrQ6V8SbA5wY5N5ZuCvZH5fJV0N/73l8F+SOU/gh087t0Ns9bZKlYGnGixY/sE13IWfTdK5WVSeb1xj8gDwT7OyndafLB9KAVOzmvB1hbtF4szlsJ98uCCtZL+nOiwo8W6u7WigQ9VqAzD7NA3uJ6y0Q692kaDgfKyBW1/0Up0BRdtUPDfTMXAImsOridFd/awWH+I6CV+VGGmsnmwDVUssJQKLXyTPvsGF343iLZL0p1rpeygvaNigckGV9Ns0xRcT4ie09UGOCrYgSrONOZb/KN/WhwpfD8hd8hYMdgOKjZwdLBj0vc+weVLoCbI85J+WCr/mspKnwcGXX5NwYVdoxUFPLge04qMty36tA1m8rOcNYOdZLENfMJ+we4KtqU7BQ4Ndl+w0zItZ/lgt1hc/i8ervqH0y0O0gctbmAYzJOGoFLGLCa8G4j+k5TbIJl1+gQXfwS/s0T3h3V+KjcFR5OudPk9rUJgHxtc5/amxQGheHsf1YqMhyz63K4VGTojbmyDTQcbifeTTtChnWvxma0cbOmk+crh7Jn0uansGyfn62BbZWXyxnuz8oQ5QIXEGhZHT96huw15NPOpDS+fXNsVXHtZ9NMRR0eg07HgbVGadKXL7xkVEswyPmvmtk7uZP2Ci+DAZ0wrEuSZ81RMlNr/bdKYlZwLkpZD+fKC5n3Od92dTym4+qDJcxvkCRogNLoruDa16HeG6D4yL0vlUudCk650+T2vQoHVgj1u5Xv1Ca6HLfpcoRUJvWcOde+KxmDWa84UjbM5yltbHBBuaJ4K+P8ZC3ZQ0qbMVTa4MVNlG7urIJSWTu7bFVzMdPgx4nKYMdCPTGXOtbQjwdvfRZffqypY8+z+io3eq09wsXzhk880zirWPltwHed/OeywtR2nisZxDWXytL3Ftks+HAWRJnkfYQz6SfOsDWYFuNHiTT2BziHvKXVIDqMgtxct3o8copQs5+DXtFv0sy4emnYkoJXyR8U7rQkevPKeComdbPRefRJ66hkkJR6x9pWCa18W7YOk55wsmp83bpJpCjOys41191UnrO8lfFSeY/FMhhFNEjtRfLnTmWuFYKeIRo6nHXeeDf/BdaXsoPU5zeZIAd9SMs7s+b2KVv49ON5G67qOIgge6tl5l9D7KdTr7Fqauehb1Sjr4IUl6VP9OUxWbUK0zURE8m0Wp2E6cjLsarGBeryBhuUvZtkw6J+hfL1ozFD3ZGXyA72uDRLz0gEleinouDevcbQOXZdxzgvRNXdb32LKQB2bpRLkQxeqKHA9M1UOu0L9/5cmLW8zKw/a/ExjEKyevlO3IKvb2fq/+fjPYWv7kcXOYHRRdpgNX8jKjs9U5B087FuHq8eh7i2LSy3+5CoT4Q6L1/mOmAffNNBeCrZqsJ8t+nLMwicPMActN5Y+Xh0xG3J0sO/AtQh91AQPncTd+5JgBz4po39mcYDye97vvH9dnHxhe4tt8jbmZ2S00d+IYDpAKjOY0maoUpkyR9gseN1T+X/CUlWpTAu6S65U/jU4mqlUKpVKpTL7+BvUZ6Bx9wi4iAAAAABJRU5ErkJggg==>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKEAAAAZCAYAAABZyE6uAAAFf0lEQVR4Xu2ZR8glRRDHy4A5Kyom1gh6ECMGxIM5IsaL6IqKeDBhQFTEVQ8GzB5ETJ9ixBVEwSymixExiwEPZsWcs/37uuubevW6e95bWT/X7R8Ub/pfNfNmpnuqk0ij0Wg0Gv8nlvVCY/5lsWCzgh0TbOGk7TPlnTscG2xDLzYiVMKvXjQcEeyHYH8Fe8D5+jg82MfBfg92vvMpSwZ7SOL1nwu2wKB7iHOCfScxXu2rYBuYGP7P+l8wvpeDfRpsRrCtgz0b7B6JccrnMniNH4N9Eexbo107FT0a9vqNxJsyWFE5qLyZ6Xgh6WIXnYooMzvYR6Z8c7AvTRlWl3i9xVN5xVRecCqizB0SY/f2jgQfl3+u/TMa3CB5vfZufgv2pxcL8DyPeLHRoV+3hxfHi17LaGQtYmuZUyFOuzqr7WbKZFgak+X5YD87LYc2wj28w+Cfi/v+xGmKj4VaIwR8ZOU+bgq2tBfnVRhTrOnFDH1dmqXUCGksuUrIaZ7LJB+D9o4rH2TKcHrS+9BGaBu15w9Xrt17Tq/Fw6US/dt7h6N2jXmGGRIfhPTP+ITjo2yAga5tCy9WKDVCuC7Y2k7rqxgg4+Ri7LlUHMfbde5JZiZ9Bad7tBHu7B0GMrnlNonnkIFXcb4cfc+qw4l3vcOwWrDLnXZwsLMl3g+QWC4OdshUhMhKwS5Juu9RFN4VmX1C4mTLsk6w+4O9FuzoYE8PuscnN/Z4TOJLXsPpP7lyH7VG6FlCYuz73uEoVZ7VT0jHm3XuSQ5M+lZO92iDqjXCX7wg3T2oMQHZaSCio/Qclr4YJkKeM6U772GJDQY+k1in50lsOEAjJM73bmT5q9IxHxQx66XyXsHeSMewkdTvcSR290KCgTw3Y1+qzyx9jNMINQv3UaoYqzPL5Xjjzj3JvkknW9S4RWLcrt5hyDVCYJJg3xl290BEpPQclr6YXAIBJmqcRwNRNk0aY0gL2nGm/FLSLFZjdq9ZVvHxc4VSyu5j1EZ4vMQ4Zsl9lCrG6gwnON6kc09yQNJ3dLrnRolxe3qH4XsvZDhMuvvyXVrpOSy1mF0kLnHlmJDh8xjzo63sdLRZrvy2xAyodlbSgUzKMUtXpwRbJOn/mAuke+A7nc/TN1C2jNIIN5fyF51D19g8tsJ0TLhN556EcRE6460arNMRx7JLCdYDLaW1Sh3bneZ0e785GArgp0vNUfsI9P4tdKdoDHssaPQctvyKxGGEN+XBFKeWy/RjwaDyXFO+WuKF9zOacqqM1/L7GiEDZD/O7BsTUim5a6JpY2atkfKczo4PlRjHTkSO5WS4cdSui+/CjFY7R9daS8svjPFKXCPD1143aaM0wg9M2WMzKdn9RYnn8E7mmIu8kOBr4OInS9x2elXiixmHWiOk6yWle3w8DcE2/FVlOAbQTnLlK0wZ7kv6KBDH+CfHE8GWchrxpe05fOygeK10L5o9b/WOBHWypRcNEzJ87VomtElId4w8T6ZffLmhxbZOG4taZltG4or/68GOdL5RqE02tBK82a6ZMZ3qFmJuN2XGbj4ml/Uo5zJ8DmaBxPvZ7YmS32LU+9zB6Xcl3ZN7LmapGs8SSgl/nudeGY6hkaDllsV0Jgy6e8WHpvBRaObH957xqfafg6+JfV26VuxDidtqdAnA7FQrwRvjDQv7rzQID+uFbwV7SuJ5PjMBszhm+LrkwtLNODAoZxbMuV+n3zMGIjq0IthS5FhXFnw29c/LB8WzsL7IHnJpbKmw2/S4Fw3cJ90p7511PrIcu0Rsc6LxS3Kgy8aPRvw3nGx4Rrp7vNLolHWmrfe/vvE35gOul9hDNRrThmbcRmNaWF7innKjMW086oVG499m1Jl9o9FoNBqNxqj8DQIuyZlbyoQaAAAAAElFTkSuQmCC>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKEAAAAZCAYAAABZyE6uAAAFi0lEQVR4Xu2ZZ6glRRBGyxwwYgIDrDmCCgoqKmvOCuofEQMqohhQMSCr7JowYMCEiOKuGROIImZMfwyIOYCIgmLOOWsfu/vdut/tCW8f66qvDxR35qvquT09PdVhzCqVSqVS+T+xpAqVycvCwWYEOzrY/Enba8w7Zzgm2LoqVsweCvZnsC+DHSK+EntbjO/LzRbjfwx2tvjg+GC3BVsvna8T7KZgx41FjHJmsG8tXjcb9V/Lxfwm/ued7+VgHwebEmyzYM8Gu8eG7+tTG77GD8E+D/aN064di+7HeNpt0kCjLJCO90vnnwzcRfID6ANxy6bjDdP57wP339AxfWfBXhiKaIbOS/we6kiQ4bSu+xQ0mGllve1+fw32h4oNzBvsERUnO/cHu1u0+yw2+J6iZz6y9ofiOSXYixYbP3OSxbIXO216sMuCXR/stGDzOV8XuRPuqg6H1vUXi/dRQmOh637xkZW7uCHY4ir+V2FOsYqKBeZRQchDzb5OWz9pDFUK2Yahs+uhZJ62GHeF6FqejreNOx8PuRPurA6HZl79f09Jb4uHSyz6t1aH0HaN/wxTLN4I6Z/5CceH+wDHIsE2UVFYyeLb6Zlq8bp+/pT5Kf12PZTMosHusuFMuJCNlp9mE++EO6jDwZDpudVime+DrSC+ElpfhXbE/7Y6HCsGu1S0/YOdYbE+QGK5KNgBYxFxKsOogZ4XT8pBFjP7LIuLLc9qFke814IdYTExTIjS3OMxi428sugsAmaHBy026Aaiv2uDRuh6KG2carHsUaKdk/SZ6fdq528jd6i2TvizCja4h2yMCtsPRQzoc79dMSyElNNtUO5hix0GmJPzTM+12HGATkicjm5k+avSMS8UMWuk892DvZGOgYVfWx17sYsKiWUsVsY36pZDEf1gLkbZ50TfyuK8LdPV4G1Q7gvRTrDY+T3EnSVaibzy3kkdjlInBBYJvs0wnSNDn/vtiiklEGAXgHJ5ZwA2TpqOUmjHuvOXkubxGqv7nGUzGj9HaErZfSB7loZhHc66GryJt4J9pmIDff+DxQxxu6nD8Z0KBQ62wX/qkNanLm0xOwY7VMXELBstx5wfbXnR0WbIOW1KBsw2PelAJuWYrSsWhAsmfcKcb4MbvkN8StdE2cOc4XYVA6/Y7D0UhYzFf5TQIQZyZu+CfTri2HZpQhdZ58l5Js/tmB54uu6XqQB+htQSbS9Brr+H4RSNObUHjf1Rf87zYRqhlsnTq2ylTD8umFT6IYp5Exdm81hhe6Rvz7/T4pzM8176fapg+YY45mtDFwwhbIh7fMNzzCawp+vBZw60GMeXiBJL2WjnaLsuvgsKWluZNy36m7Zf2vZdr7HRa6+etD6d8H13rvhMSiJh75UytMlsc6EKCd4GLn6ixc9Or1psmD6cHOxI0UjrV4rmaXoodATt+GTjG0UDnxW5FsOFp+k/ShDH/KfEE8EWE434ps9z+PiColpTXXL2vEUdCZ7Jpio6ZtnotdsyoU9C+YuR8mT6xVcaxbYQbVzoA/YsYXFl+Xqww8TXxHY2aGC1tol+6aFsVNDzAyoZ85UM203LufOpFmPWdlobrAKJ19UtC54HRINch21FZztJ7wv0voApRI73G++KllPutdEYOgnaqqKj5ZUw5IUkL1qGNs+ZH987zpe1fxW5cUvm9/YyrDI/tDhUY8y12DrI8P2VDpFh0qzXzba5iwOGY+/P2xV9IXtTP8p+lX6nDUUMwAdMQzjO80/NplpnVrh8bWF/kfo2zS0ztOHjKjqoJ8Mpbck+H1mOvdgPksYvLyhDNn404r+msOMZG9Txcqdznlfauf5rOn9lEnCdxRGqUplr5IxbqcwVlrb4TblSmWs8qkKl8k9T2rutVCqVSqVSmQh/ATj9zWSHLMWOAAAAAElFTkSuQmCC>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIsAAAAZCAYAAAABt923AAAFAklEQVR4Xu2ZWcxdUxTHFzVPqVBT8IlIU0oIIYKHEvMQQdsXIUhDqOgURHgwJTw0aetBYkwIYkwQCVHVCB6qIqGtNkgq5nmMsS3W317ru+v+7z53n+9KE7fZv2Tl3v1f6+y7zzlrj1ekUqlUKpsOB7FQGQ4OU1ukNi1oN4TvG4O/WRhWRqTdzfykdh6LfXhCUr3vqm1HPucStc/V1qvdTr4c30iq022d2tfBfw/5+b5Qvklta7WLrXy32uoQ853pbrjvb9V+sfIGtTNHo8tgVJnH4rCSe6jMZZJi2iTLlpJi97XyOCvvORqReFLts1B+SNKLakOpzavUdiPtD0kjCoN6YrKACaYvIx0cKcn3CDsa+ISFYeVF6fSYfqD3tk2WV6X3Ac2X3t9AeYuMdippOUrJgjYwiJ/EojJVmpPlFdKdKZL8Z5Oe41cWhpG91Z6RztDexA/22TZZEHcnaceY7iyksgPtAxYzDJosTaNBU7K8THqk1AZwgdrpLA4jfqP9kuVCtYvse5tk8SmHF4wjpp9r5T+tzLR5AaAU15QssAXsyODJ8hI7Au9LitmHHQGsbyK7ql0uqQ34BKeoPaw22YOUc9QeV7sqaJGt1O6TNN3e2O36l1mSOt1Tkhb06JwDg0r8JvslCxZ3TptkQcMQN5d0f/jXWrnpZTfpTCnuNRaUk6RzndsaSQnOeHsXsyPwtKSYB9gR4BFrf+kswrGw/sh0JBG0qyUt2rdX29w0H9md403f2cq+kXC+Vzs4lLHueiyUx8Qu0j28NiXLl2qbhTJiSslygqQ47hG4Meh4UMBfFtOkM6W411kw0EF8VIu2ewySdsmCl42YpewwsE4bYdHItf9H0zBqONeZFkH51ozmzxzfefc5cLLwj+eSBfMsv3DElJJloqS42aR7z7nFyrmHBZp0phT3BgsZdlJbIvm62iTLC5JibmOHwXVG4FtLGjonXzOHNJwNoXyIpAR3g+ZTr9/PUrUzTBuIu6R3R5BLlt+oDBBTShaMRIhDj4igR0M/38o4V+HfBH6jJUpxK1lQTmPBWCG9dbVJFkwXiIkjgbOD9O/NuA7nTxHsILkdV5KG4wWUsc45kexwi8HRxV8W54ZOPGael5SB0bxCfL/X4jjmTYvBHJxbPEYQ17Qb8rMWvAR+MAAabrSEt7kJvEjmQxaMo6S3rjYLXPiR9DlwJMHHAhFc+w5pH5seuYI0P+86IGgMRkznUCk/qzHRpjKfXnhk2UZtJmnYAfCDuEa6f2MPKjvQ2px2YguM2NziFKPbzyxK/vfADOn1lbbOSAb4t2WHwfUx8PPolxtZ8GxZQ5k7I3jOPjkeh5OsDQwqKlV2rKSYS0n3a+MfZceZFkH5DtIwgjwayphf+bp+YKGaO/CCnksi1I1je/ZB52nzQNN57bOXpCkaPmwUcmA9cT2LBK7HSBLBrofv/2bTYpuxo4S2X9CQ1OPtO3xnBd/R0v5kvJG31L6Q1GgYvi/vikhgK/appBhkP8oOTjBz1/hIgnkbL+/+bvco8L0nnekQc/1YeFDSdRjN8IkXmVtDgLfVdlT7XVIsjgXwiRcSgRYNUw3+KsBoha3uyZ3QLHx6HcFLxELWnyWSF+ATZehfSepw+D1/7vj/7FmLBUdIapO3MZ7RoI1+Yg7jhK/8j8htDiqVHqbLJnK8X9n4YGqoVFrBu8BKpREcJVQqlUqlUvlv/ANxRqv2k1NPEAAAAABJRU5ErkJggg==>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIsAAAAZCAYAAAABt923AAAE70lEQVR4Xu2ZR4htRRCGy5xFMQv6RESMKIoi4kLFHBDl6UZcGMCcE6KCCRQUDAsXJlDMAURciOkh6kLdmBUVFCPmhDn2Z3fN1Py3+5373swDZ+gPijv1V92ec7r79Knua9bpdDqducNWKnRmB9snuz7Z4UG7KPy9JPhHhdnIOclOVDFwcbIfkv2c7FiJDfGA5U56M9nKEnOOSfZZsj+TXSWxGl9ZbtPtj2RfhvjNEtdBwr802QrJji7+TcneCjnfFN2N+/862U/F/yvZQRPZw7CqnK3ibOGeZL/bZGecNDU8AYP8RPBfT/Z88FssZ7ndjYu/TPE3mMjIPJjs0+DfaXmgxqE2ESJvJFtXtN8srygK7cTJAusU/QXRYSfLsbs10OBjFWYrrcmyutUHA20NFYVnbbSDrrHR9vCXrWj7iVZjaLJwDQr5W6iYmG/tyfKM6M7uluOHiF6DVXlO0JosL1t9MNBuUVEg50bRdi26c534Dtp7KlZY3MnSWg1ak+Vp0SND1wBHJTtAxdlKa7K0OqKlO/7K0YJxXtEPK76/BpWh9p2hvNZkwa7VQAWfLE9qIPCu5ZyNNBCgvomsbblG5Bq8Vtw32V3JtvakxKHJ7k92WtAiyye71fLr9pKpof843fJD95Dlgp6Hc9pwszM5Wbgw4meJ7p1/fvFb7bR0ZSjvORUSe9vk99zetjzBFb/eWLMpD1vOuV0DAV2xNrXJIpzC+sOiM4nQzrVctK+SbOmifVdynD2KvmbxfSPhfJtsm+BTd90X/MWGf3KyitYejJbu7Gk5rk8EN4ZOR0GrnZauDOW1CnFWgVjcu60Xk2y8ycJgk7NAAwXqtHkqFmrX/33RWDWcC4oWwb+ionmf87fuPmdsspyqotVvBlq6s7nl+Bmi+5NzefFb7bR0ZSjvRRUqUMQ/ZfW2xpksj1nOuVIDBW0zQux90T4veuRM0Tgbwt/W8gR3Q/NXr9/PgmQHFm1GoFFdBaDWgdDSnaUsx3kiIjzR6EcWn3OVWjtD7TtDeWzzlf1VKLxmo22NM1l4XZATVwJnVVv408z3OJqIsIPU6zhFNI4X8Klz9hLboeRwdPF3yXPjIZ42NKSrAPxooxcOaPoeVshp7Yb8rIVBaLXPjQ7hndCCgVQ+UKGws422NU6BS5xJX+NxGz0WiPDdV0X7qOgR6smoHV/8zYKmsGI629lwX40NjbDUKUdY/R+g7Rj8FW205mEHoB1xnk1tb33xHbRxTjvZApNbK05Z3ZjsSu3/wXE2GhvaOjMZiK+kgYK2pxDX1a+2stC3quHrwwiPlk/N53BStUXG6wgKsRrETgj+1UWL4GPxh7LdihbBv0E0VpB7g8/7Vb+3MChUawde6LVJRNsc22sMXV+bWxZda58Nk/1SYmtJzKGeuFBFge+zkkTY9ej9X1a0eM3sKNE2CRqT2g9LiR0cYrvY+CfjI7DV4vcUZjIXzCfFFZ0c4anxDnsl2a+Wn9oIJ5gviQa+kvDept3bpoYnIPaO5eKMfN71i8Idlr/HasYnA1mrIYB7WM3yfZDLbz58MiARtGi8avipgNWKre4+k6lV6M8WDCJ97f3O5AU+fTy+sPzA8f8+KRq/nz1ScoHVnWvya4xnNFyjn5j7+HX+pzBhO51BqPXmzPF+Z8nCq6HTGQvdBXY6TThK6HQ6nU6nMz3+Bd1RqnSSFoSzAAAAAElFTkSuQmCC>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJcAAAAZCAYAAAA8JbzRAAAFRUlEQVR4Xu2ZZ4hmNRSGj7037KLuIiJWFBsiIvYui6L+UBQUUSzYC6KCDVQQLD8EFRVFxQoii4htEAuWX3axoFixN9be8phkvvO9X26Z2R1xZvPA4Zu8OfdObm5ycpJrVqlUKpXKVLCpCpWZyVbBrg12qNMucH9PBX+rsLDzXbAjg60SbKVghwT7dsijnfssduobwZaVuswxwT4L9kewK6SuxFcW75nt92BfuvqbpF5fKuWLgy0V7OhUvjHYm87nm6Rn+yHY18HmpfKfwQ4Y9+6GqHWmigs7+pKwdYc8yixh0Xf9VF4sldce94jcH+xTV77D4ovtQ2ngeF4PtoZov1qMWAr38YMLVk/6C6LDdhbr7tKKBj5WoRI78PJg1wfbXeraeNpGO/QqGx0MlBcvaPuIVqJrcNEGBf+NVbQYkZsG11OiZ3axWD9H9BI/qTBd2STYeioWWESFAm0vrw2uY0B6dkx65hopZ9DeVbHAZAdXU7RpGlxPiu7pagOQVuyn4nRjtsUH/cviTOHv47yDY5lg26pYoKvjSuQlUBPkWUk/OJV/S2WlzwuDLr+mwYVdrRUF8uB6XCsc71j0aZvM5Gee1YKdYLEN/MLewe4Mtll2ChwU7N5gpzjNs2Swmy0u/xcNV/3LqRYn6QMWNzBM5knDoFLGLCa8mif9LOUm6Li3LT7AcxaTbl3GFB6E684QPb+sc1O5aXA06UqX3zMqBPa0wXXZ3rI4IZTc3se0wvGgRZ/btMKhEXEDG2w62Eh8mHQGHdrZFt/ZcsEWTRobK8+uSWejBXnjlGHTtbkrkzfe48oTZl8VEqtanD2+Q3ca8mgGX3ZVmYeT1sZuFn10xtER6HQs5LYoTbrS5fesCgmiTI6a3tb0TtZvcDE48BnTigR55iwVE6X2f580olLmvKR5KF9W0HKf87fuzudrcPWhK+p0QTJMwy/UCsdGFn1OEz3PzEtTudS50KQrXX4vqlBgxWBPWPlefQbXIxZ92PSU0Ht6qHtftM+T7jldNM7mKG9hcUJkQ8upQH6esWD7J22+udIGNyZUtrGzCgV0uchhWkO9h40CPsw4DxED/YhUZonVjoTc/i66/F5TwZqj+6s2eq8+g4vlCx8faTLLW3u04DrO/zzssLUdJ4vGcQ1l8rQ9xLZOPhwFkSblPsKY9JPmeRtEBbjB4k1zAu0h7yl1iIdkkOuXdhodhlbKZzz4NO0W81kXL007EtBK+aOSO60JXrzygQqJ7W30Xn0SeuqZJCUetfaVgmtfEe2jpHtOFO34VN7QaQoRObOldfdVJ6zvJfKsPMvimQwzmiS2CxLNeaJx/sS9Dncag+8kVwZyPO24c2z4AdeScgatz2k2Rwr4anQFouePKlr5/8GxNlrXdRTB4KGenXcJvZ9CvUbXUuSib1WjrJMX5qZf9ecwWbUJ0RaJGMm3WgzDdGQfWMbeE+0XG91p0mjMf5hlw6APQ/k60YhQd7sy+YFe1waJeemAEr006Lg3n3G0Dl2Xcc4L0TV3W8diH1DHZqkE+dD5KgpcT6TysCvU578kab7NrDxos53GJFg5/U3dga5uB+v/5eM/4yiLDf0k/ZZ2YETDl1S0QaQi7+Bl3zJcPQ51HHeQjOLP0jsRbrd4Xd4R8+KbJtrLwVawOEnw5Zshv7xAD5o3lj4+HRENieh7DVyLEIGa4KWTuDOw8GOwA7+U0b+wOEH5f/Q9Gt9fH0q+sI3FNuU2+jMy2pi/iGA6QSrTGI3ulcoC4TCbAZ97Kv9PWKoqlSlBd8mVygLDnwtWKpVKpVKZOfwD7RWk6UBif50AAAAASUVORK5CYII=>

[image31]: <data:image/png;base64,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>

[image32]: <data:image/png;base64,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>

[image33]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAWCAYAAACVIF9YAAACzklEQVR4Xu2XSchPYRTGD5llnll8rEhJlCyQMiwkSUJZkJINi29jWClSQkKyYKGElQ1WspBkI2SmJEJEJFOmTOdxzvv33NN7//e/MtT91dO/53nPfb973+neT6Sm5m8xX9UhhoEZMfgf6KX6oZqgeqFaWmxucFK1h4MuqnNiF5/mhsA61RexuumhrYoTYtfdUXUKbYklqrdidctCG/isWkEeddBW1WzVFvffqUYmetjH/ST3kfeqS+RfqbaTL6OvWH9j3A9zj0Flbqvekb+oOk8e4LqewSeG++9dVQ/KfxVd48CzG+T3ecYMymQ50igzN1XfyC8Sq+lHGUA2OHiG+wBTJSzNdJMHOFQue57I3SRAtiGGAdRgVJmdniduBZ9Adip43DN7Jj6wLBcr2h3yM54nmj3gsxgSbWI1V0O+0fO0bJv1z/kj+T0ZA1VHqe2+hKUJ0g3EGXzo+QD38Q8lynIG7XEGD3m+0P0D95Fc/zhAjklxtmaqdpEvgA6uZzIIBw7Y5J5Z7FnMI2iPSwc3iXyte7yz4DEriaGeVfUPuP/+Yquqca7g6dFJOtXWix0wyDqmIrFTFK+SxHOxGrw2mjFCrA43DHAQnPVsmmfgnuo1+Y/S2gNi2XYnn60fIvb+w2YfJ7aec4XYO29Ue92jhh+6jM5iy+qJaq7qoNi18X24RvVUdcR9bvaZOaod5A+LvUcraWXkMGqoGR0bWuCCVPcPULMqhsTX4D+JTVKB3MPALyDf5tlkyo57xnRTrQ5ZbjXAF95XnmF7JNo9KwOroWvIsG2yD/iBPL5W8JXCTBGrw/IF6ZtwVKPCSIM1lrK0lxL7gwdYqshWUhYHmZmn2hxDZZvYWVFgvFhnj/23bE+lQwUjh9+RhVYDX/n4xGJ6i9W/FNtPmNEcuA51acZnFZsL4Ju0DFxb9Z/GPw1WAJ/uEQwoDporsaGmpubP8hPmhN3th1QchAAAAABJRU5ErkJggg==>

[image34]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAWCAYAAABUpxX0AAAB60lEQVR4Xu2Wuy8EURSHj4hX4hWFQi8KQtBohCDRUCjQCgpKnUgkImj8BygUGolCjUahUZF4JUQ2nhERrwSNcH655+6ePTNDtxKZL/ll7/nuuTt3Z2dmlygm5v9SxrnhfHHOOSXp00kmOS+cN86QmcsoueQ27Mkit/l65cARZ1PVB5wdVWeUJyuYGs6nqovJfRALXKmVmQAHHjWuTrxnz9QeuCUrM8EjuYNvKYez36xqzEdtOsx7BjhznDWpqzmLnG7fwFRxFjizymmmOBecZU6Dl9mUOjiCDXf5SSFqc1HeM0OpngSniFL3zCVnm9MivRjb90KNNR6c4CQVlL7xQz2pvCXKa67I9eQrNyZuUDkAV2tqTfLh0Ml5lzE+td/Ivm9QzhLlNQkK9uAesg7AtZoaWaf0yzV0Ma4h7aM2F+U1ZxTsGQ5xAK5N1eXidKjXD0KAb5Lxq9QWuGMrDacUXIsfJuuA3XSeGneQrME1ErYYaN9nag9co5WGBAXX/nSm21WdduMxPX6Axmk1AVDj2axB34iq58X9xj0F+ybE5ShXKK5fOdSVqh5XY3om13Airyt6UiggN7dL7ib9IPf4+okHck8PPN7uyH3FuNSuxd1yNsgdF38l4DCH/zYAvx24CXFcZFV8TEzMX/INg/2eGYMvxtEAAAAASUVORK5CYII=>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAWCAYAAACL6W/rAAACRklEQVR4Xu2VP0hXURTHTxFZCZFDIbRENDkVIg4WRTRGg2RT0NCSrdFoS4ODCEp/oCgagloc2sRsCoJs6B/9WQKRilDDqNRSpDpf77n5fecdSRre9D7w5XfP95z33rm/d+99IjU1NVWxX/VZ9Vv1WLW+mP5Lj+qbal512uUye1Rjku71wOUq5ZLqKsVoGk3tJg+8UY1S/Er1iGJwUNK1mb0urhQ8uD3wuKGtLs7A2+biborBoqRVUCmNUp4E8N5zF2fg3bDxDovxy9w3v3Iuqjqc5yfm4wz7F2jM3JLYzxxQnVNdk/T2sb+xfwckrZTMWdUd1SHyMtg2w6rXqjMuVwCN/HJx1Bz792jMXJHYz5xUPZVUc1h13fxj5jWrxs3bbl6/xeCo6i3FLTQu8FLSxVvIW8vEHtKYGZTk7/QJB2omAs/fc8F506q7FIfgEMFF+GeY6AGAfSyTqOayJH+DTzhQcyrwcBozX83P9Fr8RXVetZFyyzRJKmjwCVnbxFbbYzcl9j2oORF4T5yXv7fMiHmlPrFhffFtGn+Xch7Ay+sbBxDi/z0VUdMZePjYM1PmZ/h5m1TPKC4cFBn28E9GzcFrdbFvblY147wIXHs88Pwbw57iXjDGhErgA4pkJAYxH6V95jF4O0sUr5NUs4u8CDSGOv9xh/fOeXPmZzAep3gZnFR+Mlk/qA5sNh//4AvVT0mNe5DDw4ck1R8ppkvgfp9U71UfJV3bpZo074OsvHHsL8TwsSTbJD1jn/1C0eqrqamp+Td/AOpDxfdUhNuWAAAAAElFTkSuQmCC>

[image36]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAWCAYAAACCAs+RAAAB10lEQVR4Xu2WTStEURjH/xYsrCRio2QjX0LJzsrCS0KNsvASeVsoSsnCwhJfQLJQUspGTV42diLKgiy8R1IoLPA8zrnjzHOfe83djIX7q39zn9957p1zZu49M0BMTExURijdUv5CDeWY8klZFGNZZYnyDjMRTk/6cChDlA+n7oK5xp8TdSHcX6W4aeGyTpSF1EP/9N+g+6wSZSFJ6BM+g+49minjlAVbF1AmKP2pDiCXMkmZs+OSFsoBZYNSLca+ibKQR+gTPoLuPUYpr/i5BWut50mxq6PMWtdgXZmtmV1Kp1PPO8cp+KReKQPgXm3C+9C9C0+Ee+QOye5EcSuirnRqFW7qkzKAK+gTPoTuXRLQe9g1KW7TqV+s24O5xVS4wb1Xwwh6Rk6he5c26D3s+NaSblu4J+u9+GA5IGUAY9Avksmu1Qq9J5OFFDvH5TC/gT74pEEpLY2UEuG4v1Bxa8JJEoi2kB1Rh1IE0zQjB4gc6F/jDcx261EK08PbZxjDMH15jsu3rsNxDDt+7tx6yqlT2/My5Y5yQTm3r7fwf2WrMP/FJPcw/eswb1KRPuzjmXIJ817XlC2YnY6P2fEYP9DtMNf15vTAJ8Ns3d5fIQ6PxcTE/Ae+AE7qj0m9CPTvAAAAAElFTkSuQmCC>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACcAAAAaCAYAAAA0R0VGAAABnUlEQVR4Xu2WSytGQRjHn1BYsbOwIrKQjZVL2VLYsCNlY2/JQvENrFyysJCNr2CnJDYipdelKHIvG2Xh9v83M73T47y98+Y4Rzm/+nVmnuc085w5lzkiGf+QejgJl2GjF+/y2omzBj/hKeyHzXAB3sBOm0sFTvwBa3QCTIvJH+pEErxJ8VVhfkgHf5tnMRNX64SiWPGx0yZm0hOdiCDx4t7FTBr1nKUOC0t8RUKJs7gGuA9zKn6p+kGUiynsTiciCL2AXTimYnOqH0zIynXAcR0sQLGxSuJczIBcxSgYv9dBMTvHIzyALV7cL64Pbkv+wqrgBlwXs+uwPWVzBeGA/AjrAtvhg4o5XBETcNG2WcyZbZNVOCjmOSTH9uhfQNBKb0r+Fr/YIycuhDt3yYvtwFGvT17F/EQ4RsSc5wgqrhTcCnMr4+Ctth81kY7xTe617TL5nv8xHLDCti9UnAzb4yxcgT22T3gOiyJbsNvLxcI8PBLzMjV5ccb8bbAWXov5L3SwuCv4BAe8eOrw+7eng3+BOngLZ2ClymVkpM4X1aFeF75SRp0AAAAASUVORK5CYII=>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAbCAYAAABIpm7EAAAAeklEQVR4XmNgGAXDAkQA8V8g/o8FJyKpA4PXUInFQLwAygaJlQNxEUIZBCxggChABs1YxMCAlQEioYMm3ggVxwBeDNglVjBgF2fYwYBdAiT2AV0QBJYxYGoQgYrxoYmDgTADqgYmKD8aSQwD2DAgwvsmEAuiSo+CIQ8AhVIhcfkOsEsAAAAASUVORK5CYII=>

[image39]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAaCAYAAABCfffNAAABCUlEQVR4Xu2TPw5BQRDGB4nEJZyAC0g0ohB6F3ABUSgkKo1EoRC1aHS4gAvoNCqJTilaKmYyuzI7dp8neYXi/ZIv2f2+2X377wGkJMgDVdBmkgxQT9RFB0lCH7DKqywE1Ta1GaKLGqGGwAPPbuylDFyb1UEIKpZtUk54Prbgjoukg5qI/hh48FF4kgbwEVHNHdVCVZ0KD77V2N346KH6wPnK9OtOhaKNmmsTmQFPsteBwd5HRgc+QqslonazhnDmQGe71KZgATzRTgfA/lWbPuKsJLQb8ujZR1IB3vI3NsATytqS8ez/UYPAxdsV/iILPVnZv4n2myJ8ThBHUxpsOBnvILyUlJR/4wVMWVSSGaGDLQAAAABJRU5ErkJggg==>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAAaCAYAAABsONZfAAAAkUlEQVR4XmNgGAVDFbgC8QYgzkOXwAZMgPg/EDtA+VVQPgxMQ2KDgS4DRIEQmjhIbDWU/RdZAgRAki/QBYHgHwNEzhyIo5ElHKAS7siCUPCIASKH7EwwAFmPIQgF1xggcpLoEg0MuDVdZMAtB5ZQRRO7B8RroXIg0IckBwagUAOFDsz9M5Dk7kPF4pHERsFwBQBRqyKsylFqowAAAABJRU5ErkJggg==>

[image41]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAyCAYAAADhjoeLAAACfklEQVR4Xu3dz6tMYRgH8CNJSYqFLCxuClmIBQvhL0ApK7FQ7MVK+QdYyFY2KFGUJcpSEpKiFCUiNrJgw8aP9zXvcd95rpk7mjuM6fOpb+d9nvecc8/c1dM9U7dpAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABjOyyECAMCIbYsNAADGy+vYAAD4H+xLOV3W8+uNCXMtNiobYwMAYBx8T7kQ6pxJdSQ2iptN/899MDYAAP6GPKAsCb31KY9Db1JcjY3K7abz+1gTN4p+wxwAwEhsSLkXm8Wy2PgPXYmN5HJsFJfK8U7TezDr1QcAGJlxH0DaV7N1BrEg5V0z8/yjoa49qtb5uhVVna+7lXK/rP/Et5SVKVNN55my1b92AQBmEQea2ZxN2RubI1I/28WULVVd6/cZ8oD0vKznpayr9mqfQ50/Y7xvrGv5Neva2GxmXpPrG6EHANBXHChau2KjOBkbI1Q/W14vrura9dgI2vu86ep2OxQbTee6Y6HuZXlsFPGaXOfvBwIADCwOFNmmUH9J+VTW7fkLUz6U9ZOmM4ScL/Vcya8fW797zkE9THmQsjVuFO3niA430z83/3WuXX8sx0HE5441AMBA8hCxJ2VpyqvurZ+94yk7St0OHKeqdXaiHPO5cyXff6och9XvHnmvXw5U550r60Hla1al7Ex5n7I7ZXvXGQAAQ1qUsrmZHnj2V3vPyrH+Tluv15b/mv9qAABMrBcpT6v6brVuX1nmYe5typlqDwCAMfI1NgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYYz8Aebd7O5FwwkQAAAAASUVORK5CYII=>

[image42]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJAAAAAaCAYAAABYbdUGAAAEV0lEQVR4Xu2ZaYhURxDHK4oaiSJGgoJBERQEYxAxaESNFyr6ySvilYBK/CIiIvkgCIsBEUMQT4j3Ld5HJCEeuCIhXqCCEbyyCx4oKioa4onWf7trpl5t787MZsg4O/2DP/v6X/Xmnd1dr5coEolEIpF6yQtWU2tGItkwl/WWddsGIkGGs3ZY0/OSNYvVmlyHHMyq1Amej1iHyd33s6wPkuHiAhchamxiNYFc3MhS4XvWU0rfp53JcAp9L0UDEhlEbb0vI34r326Qyigi0Ft+YM0jdxF/J8NBulIRX3AeyPQClbHWsMYlQyn+oeoj2DnWc+MVBbhgvQ01VF6IfZTcr9TI9AJlAjlfG0/KiKJiKutH1V5I7iL+Up5mGLlpCznoLSNYfRMZpcF/eYH6kcvpY/xvvf+x8YXOrJms5ZS+52NZ68hNicI35M5tgvKE5uRGPswymJK3JMO5E7pYGYVCzCZ3YMS3+TaKxFIj0wt0hNwHya++jYJaQMkAr7vyAF4G+D2NL3zFOkguZzrrpPc7ea836xm5Yhy1FTxMi8KnrH9VuyXV/JyzAkPoCmsyy8j98Gkb8Ej98z5/NWyuRRtZG8j13LWs1ayOVXtlD65/lzU9iLVXbelwwnzf/lx5YKT3Jxrfghz74EPe78bD+V5XbfDEtHPCHlATOiFhD4VjHVjnWVdsIA9MY71hjbeBAoHrx33IFuQf89vf+Xa3dLiKMd4fZHwLctYHPPtMDhhvqG9jvQ8fTRiB6gxqGfTEmsAJ4mBHbYCc/9CaHoxak62ZJ+wNKiQ4l73W9DSyBiUfsNRAX6bDVeC+wdf1TAjkrAx49v7sDniodyUXupwMZ4/94RChkwLwMI+HCOXni1x+e1GO6uJ2yxqcy35rkpsSEfvC+PBe+e0mvl3XrzDkLAl4dl/UaNprobax/CLx/srPChRb2Qy/6GE4gM79zHuy/jOQkkW0vYgPyY1WqPbvmNhFcl8E95U3h3WIVcH6RfkYMW+odqHBdWKKsGwiN9Xq+hBfPshfpTy0l6o2kII7E8jBl5j17L6oebR3nNVLtQFWzfHi5oQcLBcJ+GzX7UdqGw9ZF2nNKJm7lbXAb8OXtSbJmUHpXo3VcL3vKdYk1S4kcm5/2AC5jqW/dEAFJa8FhEYbtEcZLwTy7CKkfU7ghPHKqfq5If6J8WqlHaUPlosWY2fPNe9dUB74k5JfEK/JFYYCXg70ip8pvNqtL3YKJesvHSsUeMEfkPs8v8m6xbpL1R9KD3Lne8//RW6I7eRGK/xFXk1lgfATuePJsR+Te/gYwcWT0RwdG2342Acjezm5qRVFtDzXTAX7/4p9yKE21ixw0/SLBeR/Q0IlJRfa7G9F6iHykEebNkCvRO8F5awh6VDqZdL5so06AzVbJb1nvSWSfy6xrqp2G3IvAlZDy5QPMIVhSsNf1EoAC5hnyBWIKLr1Qib++fibakcikUgkEolEIpFIJFLPeQeXpVo2Bcj0fgAAAABJRU5ErkJggg==>

[image43]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABPElEQVR4Xu2UsUoDQRCGR1FE0qmQQnwFCSk0SrBJYW1QmxAEC20VtIilvoHgA1ipnYVY+ArGF/ApVBAVlfiPOye7f3b1tBPug59jvp2920uGEyn4T5SQK6SHXCMD4XKSO+QAmUKGkBpyE3R4TIp7wKjV41YPfnWk0T7OdtDh8Yickesiz+Ri6I07yDGySWt9aPMquT3zP/HGIsWCuBvWya+ZHyPPvLJIsSXuhlXyK+ZnyTMvyBFyj5yK2zMfdBj74hanyS+Zb5FnHpBFr56RxC+xYQsV8svmG+TzoPv0AAHZfzRHvm1eR/87hlmI29c3SCMm/zJ12WF2yUcfpKg8JHdp3kcHpOzV6xJ/a3W35D6JnV7rplfrJyl2Uq4vIi7gBHm3qzbq2DPnyA65CXH9Ot56fZL838mCgoJf8AEEQE/OfP22wQAAAABJRU5ErkJggg==>

[image44]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAA9UlEQVR4Xu2UzQoBURiGP2XLhuI6lHAhrkGIKBt3YOEOrKwspNyFnVIuQLGRDVv/79fMcObF/BQLNU890Xu+Oa+ZjhGJ+Ec6sMqhDz14gmc4pDUXI3iEN9uae9mTA8zZ31Py3MOXMEUFuIUJI8uLtcfcyN4Spkgfmc4vKQ90V2GKlDFMUvaTIqYk1h76AzzRoTqHIdDrrxy+QwcbHAZkAi8cfkKLmhwGoAL3HHqhRS0OfSjCFWWBDkObQ5syzFCWhQvKFM+itFgDfV4AMXk9tnEjY2fG3AM9iju4gWv7U//x+loymYr1LnQYyGuBY9eYi4iI+AJ3IB1GRVmN+4UAAAAASUVORK5CYII=>

[image45]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIMAAAAaCAYAAACU9O/tAAAECUlEQVR4Xu2YaahNURTHl3mIDEnJ8J4pQ5SMIb2SWSgfjB99kEJIkuKJD6YiGaLwTCkz+WQoUqZChC9IypBZQsaw/u29u+ust++759533333evtX/+7e/7XPOfucs8/ea1+iQCAQCAQy5gerkTYDNY9lrL+sFzrwH1BLGzEYxzqszRR0Yd0g8xwvqFhBgRtwqq9iyUBbPLR8pSuZ2e6ADiRhCeszJZ7DkWi4QkrIHOPoo+oFwwLWatZyMjfwJBr20ptM29o6kAe4F7NBB9Ig3cGA9nOU95N1XXl5jxzB7quoIzwfJyn/Rv5MMn3C4K4s6QyG1mTa41dyzvoFwyyKfkFrydzAA+FJxpBZGtDmO2s8a1ikRe7B9I7+TNGBSpDOYFhB/pdeRn7fMZm1lLXH1huwFrJKWfVcIzL3hzbISTR49lfI5Cq4/0fRcHr4OutmBx+LKPHwD9n6iEiL3LGZTD+qYjCmMxhOkf95bSO/71hMJmFHGwyMedZfY70i1kXrdbfeRFsH+IgPivoMqvh6FYKRhA5rtpA5KUabD5cvZJKlZ4sSMn2YpgNZAuc+qs0kXCb/S3CDta0OCPC1o43eucD74/E+qPpsUXdeRlR0IGLJ4scpeSzXYECjL5ihsgnOifuMA2ZI3/PYSsavqwOCYjJtipQPb7vHk9e5ZutPqfygSAus/fu0KSgjcyHffhn+e21WM0PJ9Gu9DmQIznVCm0lIljPsJr8vaUemjU4+ffeiBwN4LHyoNBqOhz6pD9/FAbxsZOxVQWcyia1cSzMB94hcIA5uIOoXGmc3gSUEbVoqH946jyfP10aUcfwbSn29cgyheFMgvgycXLbtZT33/8JwSiSQK1n3WT1tHe2a2fI91jfWBNZeKr//fsXaz7qj/ExpznrLOq8DMUHfT2vTMoDVV3lojyRQ8oWia7yPYjLHtlI+vFQzg+/Fw0v1t0AEd9J05MBWUtY/ivJoMgkptqcAgwj/xE21dRzXwpbPsPrbMpKnTrYsz50NsEXTAy8V+AcW/cCWzYd+JgCzwG9RR3KNNsXC89GPTLseyoenl3F9XZTPirrzYtOBoi85rjbhYAv2svB8X7HszCRRBjL2jjXfljGlI4YvuTqZS6Zf2O49Yz0nM2NhRpNgwPt2YXdZX1nHyNxPqi03lrOXZK6FX/x1jqQT13TX/8RqT2YJcB76CHCNkfYXwrUxI+YN8oW/FuXpZLJfB9o1sWV8Rd1Yt6n6B0QgSzRm/bLlpqzBIvaQEjPBKEpMb1cpkbV3ZK2y5VQ0JLNkxdFYe0wgx9xkXWJtVD5mgp1k/sjaIXwkmEi0brF2CT8VWNcHxdRAe0wgT5DLR6CGgnwAMwKSHySvgUAgEAgEAoEC4h/Q9C2p5BKx+gAAAABJRU5ErkJggg==>