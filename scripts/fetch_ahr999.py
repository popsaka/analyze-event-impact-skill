#!/usr/bin/env python3
"""Fetch BTC AHR999 + popular micro indicators in one command.

Priority for AHR999:
1) Coinglass public endpoint (if available)
2) Coinglass OpenAPI (if API key provided)
3) Local formula fallback (CoinGecko price history + public AHR999 formula)

Also outputs a micro indicator pack (best effort):
- Fear & Greed Index
- RSI(14, daily)
- MA200 deviation
- Binance funding rate (8h)
- Binance OI 1d change

Usage:
  python3 scripts/fetch_ahr999.py
  python3 scripts/fetch_ahr999.py --symbol BTC --pretty

Env:
  COINGLASS_API_KEY / COINGLASS_OPEN_API_KEY (optional)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


@dataclass
class FetchResult:
    provider: str
    ok: bool
    value: float | None
    ts: str | None
    raw: dict[str, Any] | None
    error: str | None = None


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _safe_float(v: Any) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _find_latest_ahr999(obj: Any) -> tuple[float | None, str | None]:
    best_value = None
    best_ts = None

    def walk(node: Any) -> None:
        nonlocal best_value, best_ts
        if isinstance(node, dict):
            for key in ("ahr999", "AHR999", "ahr_999", "value"):
                if key in node:
                    fv = _safe_float(node.get(key))
                    if fv is not None:
                        best_value = fv
                        ts = node.get("date") or node.get("timestamp") or node.get("time")
                        if ts is not None:
                            best_ts = str(ts)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in reversed(node):
                if isinstance(item, dict):
                    if "ahr999" in item or "AHR999" in item:
                        fv = _safe_float(item.get("ahr999") if "ahr999" in item else item.get("AHR999"))
                        if fv is not None:
                            best_value = fv
                            ts = item.get("date") or item.get("timestamp") or item.get("time")
                            if ts is not None:
                                best_ts = str(ts)
                            return
                walk(item)

    walk(obj)
    return best_value, best_ts


def fetch_coinglass_public(symbol: str) -> FetchResult:
    url = "https://capi.coinglass.com/api/index/v2/ahr999"
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.coinglass.com/pro/i/ahr999",
        "Origin": "https://www.coinglass.com",
        "Accept-Language": "en-US,en;q=0.9",
    }
    params = {"symbol": symbol, "coin": symbol, "size": 300, "resolution": 7}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        data = r.json()
    except Exception as e:
        return FetchResult("coinglass-public", False, None, None, None, f"request_error: {e}")

    value, ts = _find_latest_ahr999(data)
    if value is not None:
        return FetchResult("coinglass-public", True, value, ts, data)

    return FetchResult(
        "coinglass-public",
        False,
        None,
        None,
        data,
        "no_ahr999_field_in_response",
    )


def fetch_coinglass_openapi(symbol: str, api_key: str) -> FetchResult:
    candidates = [
        "https://open-api-v4.coinglass.com/api/index/ahr999",
        "https://open-api.coinglass.com/public/v2/index/ahr999",
        "https://open-api.coinglass.com/public/v2/index/arh999",
    ]
    headers = {
        "accept": "application/json",
        "coinglassSecret": api_key,
        "CG-API-KEY": api_key,
        "X-API-KEY": api_key,
        "User-Agent": UA,
    }

    last_error = None
    for url in candidates:
        try:
            r = requests.get(url, headers=headers, params={"symbol": symbol}, timeout=20)
            data = r.json()
        except Exception as e:
            last_error = f"{url}: {e}"
            continue

        value, ts = _find_latest_ahr999(data)
        if value is not None:
            return FetchResult("coinglass-openapi", True, value, ts, data)

        code = str(data.get("code", "")) if isinstance(data, dict) else ""
        msg = str(data.get("msg", "")) if isinstance(data, dict) else ""
        last_error = f"{url}: code={code} msg={msg or 'no_data'}"

    return FetchResult("coinglass-openapi", False, None, None, None, last_error or "unknown_error")


def _fetch_coingecko_btc_260d() -> tuple[float, int, list[float]]:
    """Fetch BTC spot+history with provider fallback.

    Returns: current_price_usd, last_updated_epoch, daily_closes
    Priority: CoinGecko -> Binance
    """
    # 1) CoinGecko
    try:
        sp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "bitcoin",
                "vs_currencies": "usd",
                "include_last_updated_at": "true",
            },
            timeout=20,
        ).json()["bitcoin"]
        current_price = float(sp["usd"])
        last_updated = int(sp.get("last_updated_at") or time.time())

        hist = requests.get(
            "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
            params={"vs_currency": "usd", "days": 260, "interval": "daily"},
            timeout=25,
        ).json()["prices"]
        closes = [float(p[1]) for p in hist if p and len(p) >= 2]
        if len(closes) >= 200:
            return current_price, last_updated, closes
    except Exception:
        pass

    # 2) Binance fallback
    ticker = requests.get(
        "https://api.binance.com/api/v3/ticker/price",
        params={"symbol": "BTCUSDT"},
        timeout=20,
    ).json()
    current_price = float(ticker["price"])
    last_updated = int(time.time())

    kl = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": "BTCUSDT", "interval": "1d", "limit": 300},
        timeout=25,
    ).json()
    closes = [float(x[4]) for x in kl if isinstance(x, list) and len(x) >= 5]
    if len(closes) < 200:
        raise RuntimeError("insufficient_history_from_all_providers")
    return current_price, last_updated, closes


def fetch_local_formula(symbol: str) -> FetchResult:
    if symbol.upper() != "BTC":
        return FetchResult("local-formula", False, None, None, None, "local formula currently supports BTC only")

    try:
        current_price, last_updated, closes = _fetch_coingecko_btc_260d()

        if len(closes) < 200:
            return FetchResult("local-formula", False, None, None, None, "insufficient_history_for_200d")

        last200 = closes[-200:]
        if any(x <= 0 for x in last200):
            return FetchResult("local-formula", False, None, None, None, "non_positive_price_in_history")

        geometric_mean_last_200 = math.exp(statistics.fmean(math.log(x) for x in last200))

        base_date = datetime(2009, 1, 3, tzinfo=timezone.utc)
        now_dt = datetime.fromtimestamp(last_updated, tz=timezone.utc)
        coin_age_days = (now_dt.date() - base_date.date()).days
        predicted_price = 10 ** (5.84 * math.log10(coin_age_days) - 17.01)

        ahr999 = (current_price / predicted_price) * (current_price / geometric_mean_last_200)

        raw = {
            "current_price": current_price,
            "cost_200day": geometric_mean_last_200,
            "exp_growth_valuation": predicted_price,
            "coin_age_days": coin_age_days,
            "formula": "ahr999=(price/predicted_price)*(price/cost_200day)",
        }
        return FetchResult(
            "local-formula-coingecko",
            True,
            float(ahr999),
            datetime.fromtimestamp(last_updated, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            raw,
        )
    except Exception as e:
        return FetchResult("local-formula", False, None, None, None, f"request_or_calc_error: {e}")


def fetch_micro_signals(symbol: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ok": True,
        "symbol": symbol.upper(),
        "fetchedAt": _now_iso(),
        "fearGreed": None,
        "rsi14": None,
        "ma200": None,
        "ma200DeviationPct": None,
        "fundingRate8hPct": None,
        "oi1dValueChangePct": None,
        "errors": [],
    }

    # Fear & Greed
    try:
        fg = requests.get("https://api.alternative.me/fng/?limit=1&format=json", timeout=15).json()["data"][0]
        out["fearGreed"] = {
            "value": int(fg["value"]),
            "classification": fg.get("value_classification"),
            "timestamp": datetime.fromtimestamp(int(fg["timestamp"]), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    except Exception as e:
        out["errors"].append(f"fearGreed_error: {e}")

    # RSI14 + MA200 deviation from CoinGecko
    try:
        if symbol.upper() != "BTC":
            raise RuntimeError("coingecko micro calc currently supports BTC")
        current_price, last_updated, closes = _fetch_coingecko_btc_260d()
        if len(closes) < 200:
            raise RuntimeError("insufficient_close_data_for_ma200")
        ma200 = sum(closes[-200:]) / 200
        out["ma200"] = ma200
        out["ma200DeviationPct"] = (current_price / ma200 - 1) * 100

        if len(closes) < 15:
            raise RuntimeError("insufficient_close_data_for_rsi14")
        changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        period = 14
        gains = [max(c, 0) for c in changes]
        losses = [max(-c, 0) for c in changes]
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 999
        rsi14 = 100 - (100 / (1 + rs))
        out["rsi14"] = rsi14
        out["coingeckoTs"] = datetime.fromtimestamp(last_updated, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        out["errors"].append(f"micro_coingecko_error: {e}")

    # Binance funding + OI
    try:
        if symbol.upper() == "BTC":
            market = "BTCUSDT"
        else:
            market = f"{symbol.upper()}USDT"

        f = requests.get(
            "https://fapi.binance.com/fapi/v1/premiumIndex",
            params={"symbol": market},
            timeout=15,
        ).json()
        out["fundingRate8hPct"] = float(f["lastFundingRate"]) * 100

        oh = requests.get(
            "https://fapi.binance.com/futures/data/openInterestHist",
            params={"symbol": market, "period": "1d", "limit": 7},
            timeout=15,
        ).json()
        if isinstance(oh, list) and len(oh) >= 2:
            oi1 = float(oh[-1]["sumOpenInterestValue"])
            oi0 = float(oh[-2]["sumOpenInterestValue"])
            out["oi1dValueChangePct"] = (oi1 / oi0 - 1) * 100
    except Exception as e:
        out["errors"].append(f"micro_binance_error: {e}")

    if out["errors"]:
        out["ok"] = False
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch BTC AHR999 + micro signals")
    ap.add_argument("--symbol", default="BTC", help="Asset symbol, default BTC")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = ap.parse_args()

    symbol = args.symbol.upper()

    out: dict[str, Any] = {
        "ok": False,
        "symbol": symbol,
        "fetchedAt": _now_iso(),
        "provider": None,
        "ahr999": None,
        "timestamp": None,
        "raw": None,
        "microSignals": None,
        "notes": [],
        "errors": [],
    }

    primary = fetch_coinglass_public(symbol)
    if primary.ok:
        out.update(
            {
                "ok": True,
                "provider": primary.provider,
                "ahr999": primary.value,
                "timestamp": primary.ts,
                "raw": primary.raw,
            }
        )
    else:
        out["errors"].append({"provider": primary.provider, "error": primary.error})

    if not out["ok"]:
        key = os.getenv("COINGLASS_API_KEY") or os.getenv("COINGLASS_OPEN_API_KEY")
        if key:
            alt = fetch_coinglass_openapi(symbol, key)
            if alt.ok:
                out.update(
                    {
                        "ok": True,
                        "provider": alt.provider,
                        "ahr999": alt.value,
                        "timestamp": alt.ts,
                        "raw": alt.raw,
                    }
                )
            else:
                out["errors"].append({"provider": alt.provider, "error": alt.error})
        else:
            out["notes"].append("Set COINGLASS_API_KEY (or COINGLASS_OPEN_API_KEY) to enable OpenAPI fallback.")

    if not out["ok"]:
        local = fetch_local_formula(symbol)
        if local.ok:
            out.update(
                {
                    "ok": True,
                    "provider": local.provider,
                    "ahr999": local.value,
                    "timestamp": local.ts,
                    "raw": local.raw,
                }
            )
            out["notes"].append("AHR999 computed via public formula fallback.")
        else:
            out["errors"].append({"provider": local.provider, "error": local.error})

    # Always attempt micro signals pack
    micro = fetch_micro_signals(symbol)
    out["microSignals"] = micro
    if not micro.get("ok", True):
        out["notes"].append("Some micro signals failed to fetch; see microSignals.errors.")

    if not out["ok"]:
        out["notes"].append(
            "AHR999 unavailable from all configured sources; use MA200 deviation + Fear&Greed + RSI as temporary micro anchors."
        )

    print(json.dumps(out, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
