from typing import Optional

DEFAULT_TRADINGVIEW_LOGO = "https://s3.tradingview.com/userpics/6171439-mFQX_big.png"

FOREX_ICONS = {
    "USDJPY": "https://flagcdn.com/w160/jp.png",
    "EURUSD": "https://flagcdn.com/w160/eu.png",
    "GBPUSD": "https://flagcdn.com/w160/gb.png",
    "AUDUSD": "https://flagcdn.com/w160/au.png",
    "USDCAD": "https://flagcdn.com/w160/ca.png",
    "USDCHF": "https://flagcdn.com/w160/ch.png",
    "NZDUSD": "https://flagcdn.com/w160/nz.png",
    "EURGBP": "https://flagcdn.com/w160/gb.png",
    "EURJPY": "https://flagcdn.com/w160/jp.png",
    "GBPJPY": "https://flagcdn.com/w160/jp.png",
    "AUDJPY": "https://flagcdn.com/w160/jp.png",
    "CADJPY": "https://flagcdn.com/w160/jp.png",
    "CHFJPY": "https://flagcdn.com/w160/jp.png",
    "EURAUD": "https://flagcdn.com/w160/au.png",
    "EURCAD": "https://flagcdn.com/w160/ca.png",
    "EURCHF": "https://flagcdn.com/w160/ch.png",
    "GBPAUD": "https://flagcdn.com/w160/au.png",
    "GBPCAD": "https://flagcdn.com/w160/ca.png",
    "GBPCHF": "https://flagcdn.com/w160/ch.png",
    "AUDCAD": "https://flagcdn.com/w160/ca.png",
    "AUDCHF": "https://flagcdn.com/w160/ch.png",
    "AUDNZD": "https://flagcdn.com/w160/nz.png",
    "CADCHF": "https://flagcdn.com/w160/ch.png",
    "NZDCAD": "https://flagcdn.com/w160/ca.png",
    "NZDCHF": "https://flagcdn.com/w160/ch.png",
    "NZDJPY": "https://flagcdn.com/w160/jp.png",
}

CRYPTO_ICONS = {
    "BTC": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
    "ETH": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
    "SOL": "https://assets.coingecko.com/coins/images/4128/large/solana.png",
    "XRP": "https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png",
    "BNB": "https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png",
    "DOGE": "https://assets.coingecko.com/coins/images/5/large/dogecoin.png",
    "ADA": "https://assets.coingecko.com/coins/images/975/large/cardano.png",
    "AVAX": "https://assets.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite_Trans.png",
    "LINK": "https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png",
    "DOT": "https://assets.coingecko.com/coins/images/12171/large/polkadot.png",
    "MATIC": "https://assets.coingecko.com/coins/images/4713/large/polygon.png",
    "POL": "https://assets.coingecko.com/coins/images/4713/large/polygon.png",
    "SHIB": "https://assets.coingecko.com/coins/images/11939/large/shiba.png",
    "LTC": "https://assets.coingecko.com/coins/images/2/large/litecoin.png",
    "NEAR": "https://assets.coingecko.com/coins/images/10365/large/near.png",
    "SUI": "https://assets.coingecko.com/coins/images/26375/large/sui-ocean-square.png",
    "APT": "https://assets.coingecko.com/coins/images/26455/large/aptos_round.png",
    "PEPE": "https://assets.coingecko.com/coins/images/29850/standard/pepe-token.jpeg", 
    "TRX": "https://assets.coingecko.com/coins/images/1094/large/tron-logo.png",
    "UNI": "https://assets.coingecko.com/coins/images/12504/large/uniswap-uni.png",
    "ATOM": "https://assets.coingecko.com/coins/images/1481/large/cosmos_hub.png",
    "XLM": "https://assets.coingecko.com/coins/images/100/large/Stellar_symbol_black_RGB.png",
    "BCH": "https://assets.coingecko.com/coins/images/780/large/bitcoin-cash-circle.png",
    "RENDER": "https://assets.coingecko.com/coins/images/11636/large/rndr.png",
    "INJ": "https://assets.coingecko.com/coins/images/12882/large/Secondary_Symbol.png",
    "USDT": "https://assets.coingecko.com/coins/images/325/large/Tether.png",
    "USDC": "https://assets.coingecko.com/coins/images/6319/large/usdc.png",
}

COMMODITIES_AND_INDICES = {
    "DXY": "https://flagcdn.com/w160/us.png",
    "XAUUSD": "https://assets.coingecko.com/coins/images/10481/large/Tether_Gold.png",
    "GOLD": "https://assets.coingecko.com/coins/images/10481/large/Tether_Gold.png",
    "XAGUSD": "https://flagcdn.com/w160/un.png",
    "SILVER": "https://flagcdn.com/w160/un.png",
    "SPY": "https://flagcdn.com/w160/us.png",
    "SPX": "https://flagcdn.com/w160/us.png",
    "QQQ": "https://flagcdn.com/w160/us.png",
    "NDX": "https://flagcdn.com/w160/us.png",
    "US30": "https://flagcdn.com/w160/us.png",
    "DJI": "https://flagcdn.com/w160/us.png",
}

def resolve_asset_icon(symbol: str, raw_symbol: str = "") -> str:
    candidate = (raw_symbol or symbol or "").upper().replace(":", "").strip()

    clean_pair = candidate.replace("/", "").strip()
    if clean_pair in FOREX_ICONS:
        return FOREX_ICONS[clean_pair]

    if clean_pair in COMMODITIES_AND_INDICES:
        return COMMODITIES_AND_INDICES[clean_pair]

    base_coin = candidate
    if "/" in candidate:
        base_coin = candidate.split("/")[0].strip()
    else:
        for quote in ("USDT", "USDC", "BUSD", "USD", "EUR", "GBP", "JPY", "BTC", "ETH"):
            if candidate.endswith(quote) and len(candidate) > len(quote):
                base_coin = candidate[:-len(quote)]
                break

    if base_coin in CRYPTO_ICONS:
        return CRYPTO_ICONS[base_coin]

    if candidate in CRYPTO_ICONS:
        return CRYPTO_ICONS[candidate]

    return DEFAULT_TRADINGVIEW_LOGO