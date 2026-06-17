from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from backend.simulation import LOCATIONS, calculate_weather


KMA_KIM_GRID_URL = "https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-kim_nc_xy_txt2"


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
    tmfc_override = os.getenv("KMA_KIM_TMFC", "").strip()
    hf = os.getenv("KMA_KIM_HF", "0")
    level = os.getenv("KMA_KIM_LEVEL", "0")
    group = os.getenv("KMA_KIM_GROUP", "KIMG")
    nwp = os.getenv("KMA_KIM_NWP", "NE57")
    data = os.getenv("KMA_KIM_DATA", "U")
    name = os.getenv("KMA_KIM_NAME", "t2m")
    kim_map = os.getenv("KMA_KIM_MAP", "R")

    last_error: Exception | None = None
    tmfc_values = [tmfc_override] if tmfc_override else recent_tmfc_utc_values()
    for tmfc in tmfc_values:
        params = {
            "group": group,
            "nwp": nwp,
            "data": data,
            "name": name,
            "map": kim_map,
            "tmfc": tmfc,
            "hf": hf,
            "level": level,
            "disp": "A",
            "help": "0",
            "authKey": auth_key,
        }

        try:
            with httpx.Client(timeout=12) as client:
                response = client.get(KMA_KIM_GRID_URL, params=params)
            ensure_kma_success(response)
            value = parse_grid_value(response.text, location)
            break
        except ValueError as exc:
            last_error = exc
    else:
        raise ValueError(f"KIM response did not contain usable grid data: {last_error}")

    return {
        "tmfc": tmfc,
        "hf": hf,
        "rawValues": [value],
        "temperature": normalize_temperature(value),
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


def parse_grid_value(text: str, location: dict[str, Any]) -> float:
    header = parse_grid_header(text)
    rows = parse_grid_rows(text)
    if not rows:
        raise ValueError("KIM response did not contain grid rows")

    if header is None:
        first_row = next(iter(rows.values()))
        return first_row[0]

    x_count, y_count, lon1, lat1, lon2, lat2 = header
    col = nearest_index(float(location["longitude"]), lon1, lon2, x_count)
    row = nearest_index(float(location["latitude"]), lat1, lat2, y_count)

    values = rows.get(row)
    if not values:
        raise ValueError(f"KIM response did not contain row {row}")
    if col > len(values):
        raise ValueError(f"KIM response row {row} did not contain column {col}")

    return values[col - 1]


def parse_grid_header(text: str) -> tuple[int, int, float, float, float, float] | None:
    match = re.search(
        r"i\s*=\s*(\d+),\s*j\s*=\s*(\d+),\s*map\s*=\s*\w+\s*"
        r"\(lon1\s*=\s*([-+]?\d+(?:\.\d+)?),\s*lat1\s*=\s*([-+]?\d+(?:\.\d+)?),\s*"
        r"lon2\s*=\s*([-+]?\d+(?:\.\d+)?),\s*lat2\s*=\s*([-+]?\d+(?:\.\d+)?)",
        text,
    )
    if not match:
        return None

    return (
        int(match.group(1)),
        int(match.group(2)),
        float(match.group(3)),
        float(match.group(4)),
        float(match.group(5)),
        float(match.group(6)),
    )


def parse_grid_rows(text: str) -> dict[int, list[float]]:
    rows: dict[int, list[float]] = {}
    for match in re.finditer(r"#\s*j\s*=\s*(\d+)\s+(.*?)(?=#\s*j\s*=|$)", text, re.S):
        rows[int(match.group(1))] = parse_ascii_values(match.group(2))
    return rows


def nearest_index(value: float, start: float, end: float, count: int) -> int:
    if count <= 1 or start == end:
        return 1
    ratio = (value - start) / (end - start)
    index = round(ratio * (count - 1)) + 1
    return max(1, min(count, index))


def normalize_temperature(value: float) -> float:
    # KIM fields may be Kelvin depending on the selected variable. Keep Celsius if already plausible.
    if value > 170:
        return value - 273.15
    return value


def latest_tmfc_utc() -> str:
    now = datetime.now(timezone.utc)
    cycle_hour = max(hour for hour in (0, 6, 12, 18) if hour <= now.hour)
    return now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0).strftime("%Y%m%d%H")


def recent_tmfc_utc_values(limit: int = 8) -> list[str]:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    cycle_hour = max(hour for hour in (0, 6, 12, 18) if hour <= now.hour)
    cursor = now.replace(hour=cycle_hour)
    values: list[str] = []
    for _ in range(limit):
        values.append(cursor.strftime("%Y%m%d%H"))
        cursor -= timedelta(hours=6)
    return values
