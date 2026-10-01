import time
import logging
from typing import Optional, Dict, Any, Tuple
import pypresence
from config import Config
from tradingview_detector import ChartInfo
from asset_icons import resolve_asset_icon, DEFAULT_TRADINGVIEW_LOGO

logger = logging.getLogger("TradingViewRPC")

class DiscordPresenceManager:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc: Optional[pypresence.Presence] = None
        self.is_connected: bool = False
        
        self.current_symbol: Optional[str] = None
        self.start_timestamp: Optional[int] = None

        self.last_payload_hash: Optional[Tuple] = None
        self.last_update_time: float = 0.0

        self._last_warn_time: float = 0.0

    def connect(self) -> bool:
        if self.is_connected and self.rpc:
            return True

        try:
            self.rpc = pypresence.Presence(self.client_id)
            self.rpc.connect()
            self.is_connected = True
            self.last_payload_hash = None
            logger.info("Conectado exitosamente con Discord RPC.")
            return True
        except (pypresence.DiscordNotFound, FileNotFoundError):
            self._log_warn_debounced("Discord no se encuentra en ejecución. Esperando apertura de Discord...")
            self._reset_connection()
            return False
        except pypresence.InvalidID:
            logger.error(f"El DISCORD_CLIENT_ID '{self.client_id}' es inválido o no existe en Developer Portal.")
            self._reset_connection()
            return False
        except Exception as e:
            self._log_warn_debounced(f"No se pudo conectar a Discord ({type(e).__name__}): {e}")
            self._reset_connection()
            return False

    def _reset_connection(self):
        self.is_connected = False
        self.last_payload_hash = None
        if self.rpc:
            try:
                self.rpc.close()
            except Exception:
                pass
            self.rpc = None

    def _log_warn_debounced(self, message: str, cooldown: float = 30.0):
        now = time.time()
        if now - self._last_warn_time >= cooldown:
            logger.warning(message)
            self._last_warn_time = now

    def _build_payload(self, chart: ChartInfo) -> Dict[str, Any]:
        vars_dict = {
            "symbol": chart.symbol or "TradingView",
            "raw_symbol": chart.raw_symbol or "TradingView",
            "exchange": chart.exchange or "Mercado",
            "timeframe": chart.timeframe or "",
            "price": chart.price or "",
            "change": chart.change or ""
        }

        details = Config.DETAILS_FORMAT.format(**vars_dict).strip()

        state_parts = []
        if Config.SHOW_TIMEFRAME and chart.timeframe:
            state_parts.append(chart.timeframe)

        if Config.SHOW_EXCHANGE and chart.exchange and chart.exchange != "TradingView":
            state_parts.append(chart.exchange)

        if Config.SHOW_PRICE and chart.price:
            price_str = f"{chart.price} ({chart.change})" if chart.change else chart.price
            state_parts.append(price_str)
        elif not chart.timeframe and chart.price:
            # En TradingView Desktop, al no haber timeframe en el título, mostrar precio y variación en vivo
            price_str = f"{chart.price} ({chart.change})" if chart.change else chart.price
            state_parts.append(price_str)

        if not state_parts:
            if chart.exchange:
                state_parts.append(chart.exchange)
            else:
                state_parts.append("En vivo")

        state = " • ".join(state_parts) if state_parts else Config.STATE_FORMAT.format(**vars_dict).strip()

        details = details[:127] if details else None
        state = state[:127] if state else None

        now = int(time.time())
        symbol_key = chart.get_symbol_key()
        if self.current_symbol != symbol_key:
            self.current_symbol = symbol_key
            self.start_timestamp = now
            logger.info(f"Cambio de símbolo detectado: {chart.symbol}")

        if Config.CUSTOM_ASSET_ICONS:
            large_img = resolve_asset_icon(chart.symbol, chart.raw_symbol)
        else:
            large_img = Config.LARGE_IMAGE_KEY if Config.LARGE_IMAGE_KEY else DEFAULT_TRADINGVIEW_LOGO

        if chart.symbol and chart.symbol != "TradingView":
            large_text = chart.symbol
        else:
            large_text = Config.LARGE_TEXT

        payload: Dict[str, Any] = {
            "details": details,
            "state": state,
            "large_image": large_img,
            "large_text": large_text[:127] if large_text else None
        }

        small_img = Config.SMALL_IMAGE_KEY
        small_text = Config.SMALL_TEXT or "TradingView"
        if not small_img and chart.symbol != "TradingView":
            small_img = DEFAULT_TRADINGVIEW_LOGO

        if small_img:
            payload["small_image"] = small_img
            payload["small_text"] = small_text[:127]

        if Config.SHOW_TIMESTAMP and self.start_timestamp:
            payload["start"] = self.start_timestamp

        return payload

    def update_presence(self, chart: ChartInfo) -> bool:
        if not self.is_connected:
            if not self.connect():
                return False

        payload = self._build_payload(chart)

        payload_hash = (
            payload.get("details"),
            payload.get("state"),
            payload.get("large_image"),
            payload.get("small_image"),
            payload.get("large_text"),
            payload.get("small_text"),
            self.start_timestamp
        )

        if self.last_payload_hash == payload_hash:
            return False

        now = time.time()
        if self.last_payload_hash is not None and (now - self.last_update_time < 1.5):
            return False

        try:
            assert self.rpc is not None
            self.rpc.update(**payload)
            self.last_payload_hash = payload_hash
            self.last_update_time = now

            logger.info(
                f"Rich Presence actualizado: {payload.get('details')} | {payload.get('state')}"
            )
            return True
        except (pypresence.PipeClosed, BrokenPipeError, ConnectionResetError):
            logger.warning("Conexión con Discord perdida (Discord cerrado o reiniciado).")
            self._reset_connection()
            return False
        except Exception as e:
            logger.warning(f"Error al enviar actualización a Discord: {e}")
            self._reset_connection()
            return False

    def clear(self) -> bool:
        if not self.is_connected or not self.rpc:
            return False

        if self.last_payload_hash is None:
            return False  # Ya estaba limpio

        try:
            self.rpc.clear()
            self.last_payload_hash = None
            self.current_symbol = None
            self.start_timestamp = None
            logger.info("Rich Presence limpiado (TradingView inactivo/cerrado).")
            return True
        except Exception:
            self._reset_connection()
            return False

    def set_idle(self) -> bool:
        if not self.is_connected:
            if not self.connect():
                return False

        large_img = Config.LARGE_IMAGE_KEY if Config.LARGE_IMAGE_KEY else "https://s3.tradingview.com/userpics/6171439-mFQX_big.png"

        payload = {
            "details": "En TradingView",
            "state": "Explorando mercados",
            "large_image": large_img,
            "large_text": Config.LARGE_TEXT
        }

        payload_hash = (payload["details"], payload["state"])
        if self.last_payload_hash == payload_hash:
            return False

        try:
            assert self.rpc is not None
            self.rpc.update(**payload)
            self.last_payload_hash = payload_hash
            self.current_symbol = None
            self.start_timestamp = None
            logger.info("Rich Presence establecido en modo inactivo.")
            return True
        except Exception:
            self._reset_connection()
            return False

    def close(self):
        self.clear()
        self._reset_connection()