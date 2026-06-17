from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from backend.simulation import LOCATIONS, calculate_weather


KMA_KIM_POINT_URL = "https://apihub.kma.go.kr/api/typ06/cgi-bin/url/nph-kim_grib_pt_txt1"


class KmaKimRequestError(RuntimeError):
    """Raised when KMA API Hub rejects or cannot serve the KIM request."""


def fetch_kma_kim_weather(scenario: str, location_id: str) -> dict[str, Any]:
    location = LOCATIONS.get(location_id, LOCATIONS["seoul"])
    auth_key = os.getenv("KMA_APIHUB_AUTH_KEY", "").strip()

    if not auth_key:
        return with_fallback_note(
            scenario,
            location_id,
            "KMA_APIHUB_AUTH_KEY가 설정되지 않았습니다.",
        )

    try:
        kim_values = request_kim_values(location, auth_key)
        weather = calculate_weather(scenario, location_id, source="kma-kim")
        merged = merge_kim_values(weather, kim_values)
        return {
            **merged,
            "source": "kma-kim",
            "collectedAt": kim_values["tmfc"],
            "agentNote": (
                f"{location['name']} KMA API Hub KIM forecast data is used as "
                "weather context. Scenario constraints are still applied for demo safety."
            ),
        }
    except KmaKimRequestError as exc:
        return with_fallback_note(
            scenario,
            location_id,
            f"KMA KIM 요청 실패: {exc}",
        )
    except Exception as exc:
        return with_fallback_note(
            scenario,
            location_id,
            f"KMA KIM 처리 실패: {exc}",
        )


def request_kim_values(location: dict[str, Any], auth_key: str) -> dict[str, Any]:
    tmfc = os.getenv("KMA_KIM_TMFC", latest_tmfc_utc())
    hf = os.getenv("KMA_KIM_HF", "0")
    level = os.getenv("KMA_KIM_LEVEL", "0")
    group = os.getenv("KMA_KIM_GROUP", "KIML")
    nwp = os.getenv("KMA_KIM_NWP", "l010")
    data = os.getenv("KMA_KIM_DATA", "U")
    varn = os.getenv("KMA_KIM_VARN", os.getenv("KMA_KIM_TEMPERATURE_VARN", "2002"))

    params = {
        "group": group,
        "nwp": nwp,
        "data": data,
        "varn": varn,
        "tmfc": tmfc,
        "hf": hf,
        "lon": str(location["longitude"]),
        "lat": str(location["latitude"]),
        "level": level,
        "help": "0",
        "authKey": auth_key,
    }

    with httpx.Client(timeout=8) as client:
        response = client.get(KMA_KIM_POINT_URL, params=params)

    ensure_kma_success(response)

    values = parse_ascii_values(response.text)
    if not values:
        raise ValueError("KIM response did not contain numeric values")

    return {
        "tmfc": tmfc,
        "hf": hf,
        "rawValues": values,
        "temperature": normalize_temperature(values[0]),
    }


def merge_kim_values(weather: dict[str, Any], kim_values: dict[str, Any]) -> dict[str, Any]:
    temperature = kim_values.get("temperature")
    if temperature is None:
        return weather

    updated = {
        **weather,
        "temperature": round(float(temperature), 1),
    }
    updated["trackingLimited"] = updated["rain"] or updated["cloudCover"] >= 75 or updated["windSpeed"] >= 10
    updated["reason"] = (
        "KMA KIM forecast temperature is reflected; cloud, rain, and wind use scenario fallback until variable codes are configured."
    )
    return updated


def ensure_kma_success(response: httpx.Response) -> None:
    if response.status_code >= 400:
        raise KmaKimRequestError(describe_kma_response_error(response))

    try:
        payload = response.json()
    except ValueError:
        return

    result = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(result, dict):
        return

    status = result.get("status")
    if isinstance(status, int) and status >= 400:
        message = result.get("message", "KMA API Hub error")
        raise KmaKimRequestError(f"HTTP {status} - {message}")


def describe_kma_response_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip().replace("\n", " ")
        detail = text[:160] if text else response.reason_phrase
        return f"HTTP {response.status_code} - {detail}"

    result = payload.get("result") if isinstance(payload, dict) else None
    if isinstance(result, dict):
        status = result.get("status", response.status_code)
        message = result.get("message", response.reason_phrase)
        return f"HTTP {status} - {message}"

    return f"HTTP {response.status_code} - {response.reason_phrase}"


def with_fallback_note(scenario: str, location_id: str, note: str) -> dict[str, Any]:
    weather = calculate_weather(scenario, location_id, source="fallback")
    return {
        **weather,
        "reason": f"{weather['reason']} {note} KMA KIM 데이터를 사용할 수 없어 fallback 데이터를 사용합니다.",
        "collectedAt": "fallback 데이터 사용",
        "agentNote": f"{weather['locationName']} KMA KIM fallback: {note}",
    }


def parse_ascii_values(text: str) -> list[float]:
    values: list[float] = []
    for token in re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text):
        try:
            values.append(float(token))
        except ValueError:
            continue
    return values


def normalize_temperature(value: float) -> float:
    # KIM fields may be Kelvin depending on the selected variable. Keep Celsius if already plausible.
    if value > 170:
        return value - 273.15
    return value


def latest_tmfc_utc() -> str:
    now = datetime.now(timezone.utc)
    cycle_hour = max(hour for hour in (0, 6, 12, 18) if hour <= now.hour)
    return now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0).strftime("%Y%m%d%H")
