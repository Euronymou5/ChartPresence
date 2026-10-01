import os
import sys
import logging
import configparser
from pathlib import Path
from typing import Optional, List, Tuple

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

_parser = configparser.ConfigParser(interpolation=None)
CONFIG_FILE_LOADED: Optional[Path] = None

cfg_candidates = [
    BASE_DIR / "config.cfg",
    Path.cwd() / "config.cfg",
]

for candidate in cfg_candidates:
    if candidate.is_file():
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                raw_content = f.read()
            try:
                _parser.read_string(raw_content, source=str(candidate))
            except configparser.MissingSectionHeaderError:
                _parser.read_string(f"[DEFAULT]\n{raw_content}", source=str(candidate))
            CONFIG_FILE_LOADED = candidate
            break
        except Exception as e:
            print(f"[WARNING] No se pudo leer {candidate}: {e}")

if CONFIG_FILE_LOADED is None:
    env_candidates = [
        BASE_DIR / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in env_candidates:
        if env_path.is_file():
            try:
                from dotenv import load_dotenv
                load_dotenv(dotenv_path=env_path)
                CONFIG_FILE_LOADED = env_path
            except Exception:
                pass
            break

def _get_str(*keys: str, default: str = "") -> str:
    for key in keys:
        norm = key.lower().replace("-", "_").strip()
        for sec in _parser.sections() + [_parser.default_section]:
            if sec in _parser:
                for opt in _parser[sec]:
                    if opt.lower().replace("-", "_").strip() == norm:
                        val = _parser[sec][opt]
                        if val is not None:
                            return val.strip()

        for env_k in (key, key.upper(), key.lower(), norm):
            env_val = os.getenv(env_k)
            if env_val is not None:
                return env_val.strip()

    return default

def _get_bool(*keys: str, default: bool = False) -> bool:
    val = _get_str(*keys, default="")
    if not val:
        return default
    return val.lower() in ("true", "1", "yes", "on", "si", "s", "verdadero", "active")


def _get_float(*keys: str, default: float = 0.0) -> float:
    val = _get_str(*keys, default="")
    if not val:
        return default
    try:
        return float(val)
    except ValueError:
        return default

def _get_int(*keys: str, default: int = 0) -> int:
    val = _get_str(*keys, default="")
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default

class Config:
    CONFIG_FILE: Optional[Path] = CONFIG_FILE_LOADED

    DISCORD_CLIENT_ID: str = _get_str(
        "DISCORD_CLIENT_ID", "client_id", "application_id", "app_id",
        default="1170029929543520326"
    )

    DETECTION_INTERVAL: float = max(
        1.0,
        _get_float("DETECTION_INTERVAL", "detection_interval", "interval", default=3.0)
    )

    DETAILS_FORMAT: str = _get_str(
        "DETAILS_FORMAT", "details_format", "details",
        default="Analizando {symbol}"
    )
    STATE_FORMAT: str = _get_str(
        "STATE_FORMAT", "state_format", "state",
        default="{timeframe} • {exchange}"
    )

    SHOW_EXCHANGE: bool = _get_bool("SHOW_EXCHANGE", "show_exchange", default=True)
    SHOW_TIMEFRAME: bool = _get_bool("SHOW_TIMEFRAME", "show_timeframe", default=True)
    SHOW_PRICE: bool = _get_bool("SHOW_PRICE", "show_price", default=False)
    SHOW_TIMESTAMP: bool = _get_bool("SHOW_TIMESTAMP", "show_timestamp", default=True)

    CUSTOM_ASSET_ICONS: bool = _get_bool("CUSTOM_ASSET_ICONS", "custom_asset_icons", default=True)

    INACTIVE_BEHAVIOR: str = _get_str(
        "INACTIVE_BEHAVIOR", "inactive_behavior",
        default="idle"
    ).lower()

    LARGE_IMAGE_KEY: str = _get_str(
        "LARGE_IMAGE_KEY", "large_image_key", "large_image",
        default="https://s3.tradingview.com/userpics/6171439-mFQX_big.png"
    )
    LARGE_TEXT: str = _get_str("LARGE_TEXT", "large_text", default="TradingView")
    SMALL_IMAGE_KEY: str = _get_str("SMALL_IMAGE_KEY", "small_image_key", "small_image", default="")
    SMALL_TEXT: str = _get_str("SMALL_TEXT", "small_text", default="TradingView")

    LOG_LEVEL: str = _get_str("LOG_LEVEL", "log_level", default="INFO").upper()

    @classmethod
    def validate(cls) -> List[str]:
        warnings = []
        if not cls.DISCORD_CLIENT_ID or cls.DISCORD_CLIENT_ID == "123456789012345678":
            warnings.append(
                "DISCORD_CLIENT_ID no está configurado con un ID real. "
                "Crea una aplicación en discord.com/developers y coloca el client_id en config.cfg"
            )
        if cls.DETECTION_INTERVAL < 1.0:
            warnings.append(
                "DETECTION_INTERVAL es menor a 1.0s, se ajustó a 1.0s para evitar saturación de CPU."
            )
        return warnings