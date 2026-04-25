"""Shared test helpers for pyspthin."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "tests" / "fixtures"


def load_fixture(name: str) -> pd.DataFrame:
    return pd.read_csv(FIXTURE_DIR / name)


def load_reference(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text())


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    earth_radius_km = 6371.0088
    lon1_rad = math.radians(lon1)
    lat1_rad = math.radians(lat1)
    lon2_rad = math.radians(lon2)
    lat2_rad = math.radians(lat2)
    delta_lon = lon2_rad - lon1_rad
    delta_lat = lat2_rad - lat1_rad
    sin_lat = math.sin(delta_lat / 2.0)
    sin_lon = math.sin(delta_lon / 2.0)
    a = sin_lat**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * sin_lon**2
    c = 2.0 * math.asin(min(1.0, math.sqrt(a)))
    return earth_radius_km * c
