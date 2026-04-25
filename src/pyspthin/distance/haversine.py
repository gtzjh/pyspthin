"""Haversine distance helpers."""

from __future__ import annotations

import numpy as np

from pyspthin.distance.base import EARTH_RADIUS_KM


def to_radians(longitudes_deg: np.ndarray, latitudes_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.radians(longitudes_deg), np.radians(latitudes_deg)


def haversine_radians(
    lon1_rad: np.ndarray | float,
    lat1_rad: np.ndarray | float,
    lon2_rad: np.ndarray | float,
    lat2_rad: np.ndarray | float,
) -> np.ndarray:
    delta_lon = np.asarray(lon2_rad) - np.asarray(lon1_rad)
    delta_lat = np.asarray(lat2_rad) - np.asarray(lat1_rad)
    sin_lat = np.sin(delta_lat / 2.0)
    sin_lon = np.sin(delta_lon / 2.0)
    a = sin_lat**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * sin_lon**2
    return 2.0 * np.arcsin(np.minimum(1.0, np.sqrt(a)))


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

