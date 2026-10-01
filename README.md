# ChartPresence

Una solución moderna, ligera y de alto rendimiento en **Python** para sincronizar automáticamente tu estado de **Discord Rich Presence** con el gráfico que estás analizando en la aplicación oficial **TradingView Desktop** (`TradingView.exe`).

---

## Características Principales

- **Detección Exclusiva de TradingView Desktop**: Detecta de forma nativa e instantánea la ventana de la aplicación `TradingView.exe` instalada en tu sistema.
- **Detección en Tiempo Real del Activo**: Detecta el símbolo, par (`USD/JPY`, `EUR/USD`, `BTC/USDT`), precio en directo y variación porcentual.
- **Iconos Personalizados Dinámicos por Activo**:
  - Muestra la bandera de alta definición para Forex (ej: bandera de Japón para `USD/JPY`, Unión Europea para `EUR/USD`, Reino Unido para `GBP/USD`).
  - Muestra el logotipo oficial en PNG transparente para Criptomonedas (`BTC`, `ETH`, `SOL`, `XRP`, `DOGE`, etc.), Materias Primas (`GOLD`, `SILVER`) e Índices (`DXY`, `SPY`, `QQQ`).
  - **Fallback inteligente**: Si el activo es desconocido, muestra automáticamente el logotipo oficial de TradingView en alta resolución.
  - **Insignia TradingView**: Insignia circular oficial de TradingView en la esquina inferior.
- **Timestamp Inteligente**: Cuenta el tiempo transcurrido desde que abriste ese gráfico específico. Si cambias de activo (ej. `BTC` → `USD/JPY`), el contador se reinicia limpiamente.
- **100% Seguro y Privado**: No requiere bots de Discord, no solicita tokens de usuario, no lee cookies ni inyecta código en procesos externos. Funciona exclusivamente con las APIs oficiales y locales de Discord IPC (`named pipes`).
---

## Requisitos Previos

- **Sistema Operativo**: Windows 10 u 11 (64-bit).
- **Python**: Versión 3.9 o superior (probado y verificado en Python 3.11).
- **Discord Desktop**: La aplicación oficial de escritorio de Discord instalada y en ejecución.
- **TradingView**: Es necesario tener instalado [TradingView](https://www.tradingview.com/desktop/ "TradingView") en el pc.
---

## Configuración en Discord Developer Portal

Para que Discord muestre una presencia con el nombre "TradingView" e iconos personalizados, debes crear una aplicación en el portal de desarrolladores de Discord. **NO necesitas crear un bot ni generar ningún token.**

### Paso 1: Crear la Aplicación
1. Ve a [Discord Developer Portal](https://discord.com/developers/applications).
2. Inicia sesión con tu cuenta de Discord.
3. Haz clic en el botón azul **"New Application"**.
4. Dale el nombre **TradingView** (este será el nombre principal que aparecerá en tu perfil de Discord como *"Jugando a TradingView"*).
5. Acepta los términos y haz clic en **Create**.

### Paso 2: Obtener el Application ID (Client ID)
1. En la pestaña izquierda, selecciona **General Information**.
2. Verás un campo llamado **Application ID**.
3. Haz clic en **Copy**.
4. Pega ese número en tu archivo `config.cfg`:
   ```ini
   [Discord]
   client_id = 1170029929543520326
   ```
   
### Paso 3: Cómo comprobar que está funcionando
1. Abre tu cliente de escritorio de Discord.
2. Abre la aplicación de escritorio **TradingView Desktop** y entra en cualquier gráfico (ej: `BTCUSDT`, `USDJPY` o `DXY`).
3. Ejecuta `python main.py` o abre `TradingViewDiscordRPC.exe`.
4. En Discord, haz clic en tu avatar o abre tu perfil: verás la actividad con el título "TradingView", el par que estás analizando, el precio y variación porcentual en tiempo real, y el tiempo transcurrido.
> **Importante**: En Discord, ve a **Ajustes de Usuario** > **Privacidad de la Actividad** y asegúrate de tener activada la opción *"Mostrar la actividad actual como mensaje de estado"*.

## Opciones de Configuración (`config.cfg`)

| Sección | Clave | Valor por defecto | Descripción |
|---|---|---|---|
| `[Discord]` | `client_id` | `1170029929543520326` | Application ID de Discord Developer Portal. |
| `[Discord]` | `detection_interval` | `3.0` | Intervalo en segundos entre cada chequeo de estado. |
| `[Display]` | `details_format` | `Analizando {symbol}` | Plantilla para la primera línea de Discord RPC. |
| `[Display]` | `state_format` | `{timeframe} • {exchange}` | Plantilla para la segunda línea de Discord RPC. |
| `[Display]` | `show_exchange` | `true` | Muestra u oculta el nombre del exchange. |
| `[Display]` | `show_timeframe` | `true` | Muestra u oculta la temporalidad. |
| `[Display]` | `show_price` | `false` | Muestra el precio actual y variación porcentual en el estado. |
| `[Display]` | `show_timestamp` | `true` | Muestra el contador de tiempo transcurrido. |
| `[Display]` | `custom_asset_icons` | `true` | Asigna iconos dinámicos HD por par/activo con fallback al logo de TradingView. |
| `[Display]` | `inactive_behavior` | `idle` | `clear` oculta la presencia al cerrar TV; `idle` muestra estado en reposo. |
| `[Assets]` | `large_image_key` | `https://s3.tradingview...` | Fallback de imagen o clave personalizada en Developer Portal. |
| `[Assets]` | `large_text` | `TradingView` | Texto que se muestra al pasar el cursor sobre la imagen grande. |
| `[Assets]` | `small_image_key` | *(vacío)* | Imagen secundaria en esquina (opcional). |
| `[Assets]` | `small_text` | `TradingView` | Texto sobre la imagen pequeña. |
| `[General]` | `log_level` | `INFO` | Nivel de detalle en la consola (`INFO`, `DEBUG`, `WARNING`). |

---

## Imagenes

<img width="265" height="110" alt="image" src="https://github.com/user-attachments/assets/36b60a43-a30d-4643-b57d-4c5ad289ff61" />

## Contacto

[![discord](https://img.shields.io/badge/Discord-euronymou5-a?style=plastic&logo=discord&logoColor=white&labelColor=black&color=7289DA)](https://discord.com/users/452720652500205579)

![email](https://img.shields.io/badge/ProtonMail-mr.euron%40proton.me-a?style=plastic&logo=protonmail&logoColor=white&labelColor=black&color=8B89CC)

[![X](https://img.shields.io/twitter/follow/Euronymou51?style=plastic&logo=X&label=%40Euronymou51&labelColor=%23000000&color=%23000000)](https://x.com/Euronymou51)
