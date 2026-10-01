import sys
import time
import signal
import logging
from typing import Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import Config
from tradingview_detector import TradingViewDetector, ChartInfo
from discord_presence import DiscordPresenceManager

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TradingViewRPC")

running = True


def signal_handler(sig, frame):
    global running
    logger.info("Señal de interrupción recibida. Finalizando limpiamente...")
    running = False


def print_banner():
    cfg_name = Config.CONFIG_FILE.name if Config.CONFIG_FILE else "Por defecto"
    banner = f"""
=====================================================
   TRADINGVIEW DISCORD RICH PRESENCE (RPC)
   [Modo: Exclusivo TradingView Desktop]
=====================================================
 • Archivo Config : {cfg_name}
 • Application ID : {Config.DISCORD_CLIENT_ID}
 • Intervalo      : {Config.DETECTION_INTERVAL} segundos
 • Modo Inactivo  : {Config.INACTIVE_BEHAVIOR}
 • Timeframe / Ex : {Config.SHOW_TIMEFRAME} / {Config.SHOW_EXCHANGE}
=====================================================
Presiona Ctrl+C en cualquier momento para salir.
"""
    print(banner)


def main():
    global running

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print_banner()

    warnings = Config.validate()
    for w in warnings:
        logger.warning(w)

    logger.info("Iniciando servicios...")

    detector = TradingViewDetector()
    presence = DiscordPresenceManager(Config.DISCORD_CLIENT_ID)

    presence.connect()

    last_was_active = False

    try:
        while running:
            chart: Optional[ChartInfo] = detector.get_current_chart()

            if chart and chart.active:
                if chart.symbol == "TradingView":
                    if Config.INACTIVE_BEHAVIOR == "idle":
                        presence.set_idle()
                        last_was_active = True
                    else:
                        presence.clear()
                        last_was_active = False
                else:
                    presence.update_presence(chart)
                    last_was_active = True
            else:
                if last_was_active:
                    if Config.INACTIVE_BEHAVIOR == "idle":
                        presence.set_idle()
                    else:
                        presence.clear()
                    last_was_active = False

            time.sleep(Config.DETECTION_INTERVAL)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception(f"Error inesperado en el bucle principal: {e}")
    finally:
        logger.info("Cerrando sesión de Discord RPC y liberando recursos...")
        presence.close()
        detector.shutdown()
        logger.info("Programa finalizado correctamente.")

if __name__ == "__main__":
    main()