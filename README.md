## CORTEX DASH: Sistema de Infoentretenimiento y Telemetría Automotriz Heterogénea
> Proyecto Integrador de Ingeniería en Robótica y Sistemas Digitales, 4to Semestre <br>
> **Desarrollado por:** @LeonardoDRM & Camila Trejo <br>
> **Hardware:** STM32MP257F-DK (Dual-Core: ARM Cortex-A35 + ARM Cortex-M33)

---

### Descripción del Proyecto
**CORTEX DASH** es un prototipo funcional de un sistema de infoentretenimiento y telemetría en tiempo real para vehículos. El proyecto aborda la problemática de gestionar interfaces gráficas demandantes y lectura crítica de sensores en tiempo real, utilizando una **arquitectura de procesamiento heterogénea (AMP)**.

En lugar de usar un sistema de propósito general convencional, el proyecto divide la carga de trabajo entre dos entornos:
1. **Espacio de Usuario (Linux en Cortex-A35):** Renderiza la interfaz gráfica táctil, procesa audio multimedia y muestra la transmisión de video.
2. **Tiempo Real (Zephyr RTOS en Cortex-M33):** Lee la red de sensores físicos y gestiona datos críticos con latencia mínima.

---

## Arquitectura del Sistema
El sistema utiliza la tecnología **OpenAMP (RPMsg)** para establecer un canal de comunicación asíncrono y de baja latencia entre ambos núcleos mediante memoria compartida interna.

```text
[ SENSORES ]
  ├── BME280 (SPI)      ───>  [ Cortex-M33 ] 
  ├── VL53L0X (I2C)     ───>  (Zephyr RTOS)
  └── NEO-6M GPS (UART) ───>        │
                                    │ (OpenAMP / RPMsg)
                                    ▼
[ INTERFAZ UI ] <───────────  [ Cortex-A35 ]  <───  [ WEBCAM USB ]
(Pantalla 7" Touch)           (Linux + GTK3)
```

## Características principales
- **Reproductor de música:** Interfaz gráfica desarrollada en Python 3/GTK3 con estilos personalizados CSS y motor de audio basado en GStreamer.
- **Navegación GPS en Vivo:** Visualización dinámica de mapas y posición vehicular en tiempo real.
- **Telemetria Ambiental y Proximidad:** Monitoreo constante de temperatura, presión atmosférica (BME280) y distancia por sensor óptico de tiempo de vuelo (VL53L0X).
- **Cámara de Reversa:** Transmisión de video en vivo mediante captura de dispositivos de video V4L2 en Linux.
- **Reloj y Panel de Control:** Sincronización de fecha y hora del sistema en un panel lateral interactivo.

## Estructura del Repositorio
```text
├── musica/             # Directorio para archivos MP3 y carátulas (.jpg/.png)
├── car_interface.py    # Ventana principal e integración de la UI GTK3
├── music_player.py     # Lógica del reproductor multimedia y motor GStreamer
├── gps_map.py          # Módulo de renderizado del mapa GPS
├── stream.py           # Gestión del flujo de video para la cámara de reversa
└── README.md           # Documentación del proyecto
```

## Requisitos y Simulación
El código de este repositorio fue diseñado para ejecutarse nativamente en el entorno embebido de la tarjeta STM32MP257F-DK, pero también permite simulaciones de la interfaz gráfica en entornos de escritorio como MSYS2 (Windows) o distribuciones Linux.

## Nota:
Este repositorio contiene las versiones de desarrollo, integración y evidencias de código utilizadas durante las pruebas del reto. Sirve como registro de la evolución técnica del proyecto hasta su presentación física final.

