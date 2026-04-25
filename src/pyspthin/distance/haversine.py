"""Haversine distance helpers."""

from __future__ import annotations

from typing import cast

import numpy as np
from numpy.typing import NDArray

from pyspthin.distance.base import EARTH_RADIUS_KM

FloatArray = NDArray[np.float64]


def to_radians(
    longitudes_deg: FloatArray, latitudes_deg: FloatArray
) -> tuple[FloatArray, FloatArray]:
    return cast(
        tuple[FloatArray, FloatArray], (np.radians(longitudes_deg), np.radians(latitudes_deg))
    )


def haversine_radians(
    lon1_rad: FloatArray | float,
    lat1_rad: FloatArray | float,
    lon2_rad: FloatArray | float,
    lat2_rad: FloatArray | float,
) -> FloatArray:
    delta_lon = np.asarray(lon2_rad) - np.asarray(lon1_rad)
    delta_lat = np.asarray(lat2_rad) - np.asarray(lat1_rad)
    sin_lat = np.sin(delta_lat / 2.0)
    sin_lon = np.sin(delta_lon / 2.0)
    a = sin_lat**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * sin_lon**2
    return cast(FloatArray, 2.0 * np.arcsin(np.minimum(1.0, np.sqrt(a))))


def haversine_km(
    lon1_deg: float,
    lat1_deg: float,
    lon2_deg: float,
    lat2_deg: float,
    earth_radius_km: float = EARTH_RADIUS_KM,
) -> float:
    lon1_rad, lat1_rad = np.radians([lon1_deg, lat1_deg])
    lon2_rad, lat2_rad = np.radians([lon2_deg, lat2_deg])
    angle = haversine_radians(lon1_rad, lat1_rad, lon2_rad, lat2_rad)
    return float(angle * earth_radius_km)
