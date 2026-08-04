## CORTEX DASH: Sistema de Infoentretenimiento y Telemetría Automotriz Heterogénea
> Proyecto Integrador de Ingeniería en Robótica y Sistemas Digitales, 4to Semestre
> **Desarrollado por:** Leonardo Rodríguez & Camila Trejo
> **Hardware:** STM32MP257F-DK (Dual-Core: ARM Cortex-A35 + ARM Cortex-M33)

---

### Descripción del Proyecto
**CORTEX DASH** es un prototipo funcional de un sistema de infoentretenimiento (*Infotainment*) y telemetría en tiempo real para vehículos. El proyecto aborda la problemática de gestionar interfaces gráficas demandantes y lectura crítica de sensores en simultáneo, utilizando una **arquitectura de procesamiento heterogénea (AMP)**.

En lugar de usar un sistema de propósito general convencional, el proyecto divide la carga de trabajo entre dos entornos:
1. **Espacio de Usuario (Linux en Cortex-A35):** Renderiza la interfaz gráfica táctil, procesa audio multimedia y muestra la transmisión de video.
2. **Tiempo Real (Zephyr RTOS en Cortex-M33):** Lee la red de sensores físicos y gestiona datos críticos con latencia mínima.

---

## 🛠️ Arquitectura del Sistema

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


