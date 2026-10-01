import os
import re
import sys
import json
import time
import logging
import ctypes
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger("TradingViewRPC")

KNOWN_QUOTES = (
    "USDT", "USDC", "BUSD", "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "NZD", "BTC", "ETH"
)

COMMON_STOCKS = {
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "NFLX",
    "SPY", "QQQ", "DIA", "IWM", "VIX", "DXY", "NDX", "SPX"
}

@dataclass
class ChartInfo:
    symbol: str
    raw_symbol: str
    exchange: Optional[str] = None
    timeframe: Optional[str] = None
    price: Optional[str] = None
    change: Optional[str] = None
    layout: Optional[str] = None
    source: str = "desktop"
    active: bool = True
    updated_at: float = 0.0

    def get_unique_key(self) -> str:
        return f"{self.symbol}|{self.timeframe}|{self.exchange}|{self.price}"

    def get_symbol_key(self) -> str:
        return self.raw_symbol.upper().replace("/", "").replace(":", "").strip()

def format_symbol_pair(raw_symbol: str) -> str:
    if not raw_symbol:
        return ""

    symbol = raw_symbol.strip().upper()

    if ":" in symbol:
        symbol = symbol.split(":", 1)[1]

    if "/" in symbol:
        parts = [p.strip() for p in symbol.split("/") if p.strip()]
        if len(parts) == 2:
            return f"{parts[0]}/{parts[1]}"
        return symbol

    if symbol in COMMON_STOCKS:
        return symbol

    for quote in KNOWN_QUOTES:
        if symbol.endswith(quote) and len(symbol) > len(quote):
            base = symbol[:-len(quote)]
            if len(base) >= 2:
                return f"{base}/{quote}"
    return symbol

def format_timeframe(interval: Optional[str]) -> Optional[str]:
    if not interval:
        return None

    raw = str(interval).strip()
    upper = raw.upper()

    direct_map = {
        "1": "1m",
        "3": "3m",
        "5": "5m",
        "15": "15m",
        "30": "30m",
        "45": "45m",
        "60": "1h",
        "120": "2h",
        "180": "3h",
        "240": "4h",
        "D": "1D",
        "1D": "1D",
        "W": "1W",
        "1W": "1W",
        "M": "1M",
        "1M": "1M",
        "12M": "12M",
        "1S": "1s",
        "5S": "5s",
        "10S": "10s",
        "15S": "15s",
        "30S": "30s"
    }

    if upper in direct_map:
        return direct_map[upper]

    match_min = re.match(r'^(\d+)\s*(?:MIN|MINS|MINUTO|MINUTOS|M)$', upper)
    if match_min:
        return f"{match_min.group(1)}m"

    match_hr = re.match(r'^(\d+)\s*(?:H|HR|HRS|HORA|HORAS|HOUR|HOURS)$', upper)
    if match_hr:
        return f"{match_hr.group(1)}h"

    match_day = re.match(r'^(\d+)\s*(?:D|DIA|DIAS|DAY|DAYS)$', upper)
    if match_day:
        return f"{match_day.group(1)}D"

    match_wk = re.match(r'^(\d+)\s*(?:W|SEM|SEMANA|SEMANAS|WEEK|WEEKS)$', upper)
    if match_wk:
        return f"{match_wk.group(1)}W"

    match_mo = re.match(r'^(\d+)\s*(?:MO|MES|MESES|MONTH|MONTHS)$', upper)
    if match_mo:
        return f"{match_mo.group(1)}M"

    if raw.isdigit():
        mins = int(raw)
        if mins >= 60 and mins % 60 == 0:
            return f"{mins // 60}h"
        return f"{mins}m"

    return raw


def extract_timeframe_from_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    m = re.search(r'\b(1m|3m|5m|15m|30m|45m|1h|2h|3h|4h|1D|1W|1M|1Min|5Min|15Min|30Min)\b', text, re.IGNORECASE)
    if m:
        return format_timeframe(m.group(1))
    return None


def parse_tradingview_title(title: str, is_tv_process: bool = True) -> Optional[Dict[str, Any]]:
    if not title:
        return None

    clean = title.strip()

    if not is_tv_process and not re.search(r'tradingview', clean, re.IGNORECASE):
        return None

    if not clean or clean.lower() in ('tradingview', 'sin nombre', 'untitled'):
        return {'symbol': 'TradingView', 'raw_symbol': 'TradingView'}

    layout = None
    if ' / ' in clean:
        parts = clean.rsplit(' / ', 1)
        clean = parts[0].strip()
        layout = parts[1].strip()

    pattern = re.compile(
        r'^(?:(?P<exchange>[A-Za-z0-9_]+):)?(?P<symbol>[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)?)\s*(?:[▲▼—]\s*)?(?:(?P<price>[0-9,.]+)\s*(?:[A-Za-z]{3,4})?)?\s*(?P<change>[+-]?[0-9,.]+%?)?.*$'
    )
    m = pattern.match(clean.strip())
    if m:
        res = m.groupdict()
        res['layout'] = layout
        return res

    return None


class DesktopStorageReader:
    @staticmethod
    def get_active_tab_metadata(target_symbol: Optional[str] = None) -> Optional[Dict[str, str]]:
        try:
            local_app_data = os.getenv("LOCALAPPDATA")
            if not local_app_data:
                return None

            packages_dir = os.path.join(local_app_data, "Packages")
            if not os.path.exists(packages_dir):
                return None

            tv_dirs = [d for d in os.listdir(packages_dir) if "TradingView.Desktop" in d]
            if not tv_dirs:
                return None

            user_storage_path = os.path.join(
                packages_dir, tv_dirs[0], "LocalCache", "Roaming", "TradingView", "TVUserStorage"
            )
            if not os.path.exists(user_storage_path):
                return None

            clean_target = target_symbol.upper().replace("/", "").replace(":", "") if target_symbol else None

            for root, _, files in os.walk(user_storage_path):
                if "settings.json" in files:
                    settings_file = os.path.join(root, "settings.json")
                    with open(settings_file, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)
                    tabs_dict = data.get("tabs", {}).get("default", {})
                    for win_id, win_data in tabs_dict.items():
                        for tab in win_data.get("tabs", []):
                            if tab.get("active"):
                                symbol_info = tab.get("symbol", {})
                                charts = symbol_info.get("charts", [])
                                for ch in charts:
                                    if ch.get("active"):
                                        sym = ch.get("symbol", "")
                                        exchange = None
                                        if ":" in sym:
                                            exchange, sym = sym.split(":", 1)
                                        
                                        clean_sym = sym.upper().replace("/", "")
                                        if not clean_target or clean_sym == clean_target or clean_target in clean_sym:
                                            return {
                                                "symbol": sym,
                                                "exchange": exchange
                                            }
        except Exception as e:
            logger.debug(f"No se pudo leer settings.json de TradingView Desktop: {e}")
        return None


class NativeWindowDetector:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.hdesk = self._get_desktop_handle()

    def _get_desktop_handle(self):
        try:
            DESKTOP_ALL_ACCESS = 0x01FF
            hdesk = self.user32.OpenDesktopW("default", 0, False, DESKTOP_ALL_ACCESS)
            if hdesk:
                self.user32.SetThreadDesktop(hdesk)
            return hdesk
        except Exception:
            return None

    def get_open_windows(self) -> List[Dict[str, Any]]:
        results = []

        def enum_cb(hwnd, extra):
            if self.user32.IsWindowVisible(hwnd):
                length = self.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    self.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.strip()

                    pid = ctypes.c_ulong()
                    self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

                    if title:
                        results.append({"hwnd": hwnd, "pid": pid.value, "title": title})
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        cb = WNDENUMPROC(enum_cb)

        if self.hdesk:
            self.user32.EnumDesktopWindows(self.hdesk, cb, 0)
        else:
            self.user32.EnumWindows(cb, 0)

        return results

    def detect(self) -> Optional[ChartInfo]:
        import psutil
        windows = self.get_open_windows()

        is_tv_running = False
        chart_candidates: List[ChartInfo] = []

        try:
            fg_hwnd = self.user32.GetForegroundWindow()
            if fg_hwnd:
                fg_len = self.user32.GetWindowTextLengthW(fg_hwnd)
                if fg_len > 0:
                    buff = ctypes.create_unicode_buffer(fg_len + 1)
                    self.user32.GetWindowTextW(fg_hwnd, buff, fg_len + 1)
                    fg_title = buff.value.strip()

                    fg_pid = ctypes.c_ulong()
                    self.user32.GetWindowThreadProcessId(fg_hwnd, ctypes.byref(fg_pid))
                    try:
                        proc = psutil.Process(fg_pid.value)
                        pname = proc.name().lower()
                    except Exception:
                        pname = ""

                    # Exclusivamente TradingView Desktop
                    if pname == "tradingview.exe":
                        parsed = parse_tradingview_title(fg_title, is_tv_process=True)
                        if parsed and parsed.get("symbol") and parsed.get("symbol") != "TradingView":
                            raw_sym = parsed["symbol"]
                            return self._build_chart_info(parsed, raw_sym)
        except Exception:
            pass

        for win in windows:
            pid = win["pid"]
            title = win["title"]

            try:
                proc = psutil.Process(pid)
                pname = proc.name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

            if pname == "tradingview.exe":
                is_tv_running = True
                parsed = parse_tradingview_title(title, is_tv_process=True)
                if parsed:
                    sym = parsed.get("symbol")
                    if sym and sym != "TradingView":
                        chart = self._build_chart_info(parsed, sym)
                        chart_candidates.append(chart)

        if chart_candidates:
            return chart_candidates[0]

        if is_tv_running:
            return ChartInfo(
                symbol="TradingView",
                raw_symbol="TradingView",
                exchange="Mercados",
                source="desktop",
                active=True,
                updated_at=time.time()
            )

        return None
        
    def _build_chart_info(self, parsed: Dict[str, Any], raw_symbol: str) -> ChartInfo:
        exchange = parsed.get("exchange")
        price = parsed.get("price")
        change = parsed.get("change")
        layout = parsed.get("layout")

        if not exchange:
            enriched = DesktopStorageReader.get_active_tab_metadata(raw_symbol)
            if enriched and enriched.get("exchange"):
                exchange = enriched.get("exchange").capitalize()

        timeframe = extract_timeframe_from_text(layout) or extract_timeframe_from_text(raw_symbol)

        return ChartInfo(
            symbol=format_symbol_pair(raw_symbol),
            raw_symbol=raw_symbol,
            exchange=exchange or "TradingView",
            timeframe=timeframe,
            price=price,
            change=change,
            layout=layout,
            source="desktop",
            active=True,
            updated_at=time.time()
        )


class TradingViewDetector:
    def __init__(self, bridge_enabled: bool = False, bridge_port: int = 8765):
        self.native_detector = NativeWindowDetector()

    def get_current_chart(self) -> Optional[ChartInfo]:
        return self.native_detector.detect()

    def shutdown(self):
        pass