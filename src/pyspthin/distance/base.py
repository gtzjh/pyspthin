"""Core helpers for geodesic calculations."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

EARTH_RADIUS_KM = 6371.0088


def kilometers_to_radians(distance_km: float, earth_radius_km: float = EARTH_RADIUS_KM) -> float:
    return distance_km / earth_radius_km


def radians_to_chord_length(angle_radians: float) -> float:
    return 2.0 * math.sin(angle_radians / 2.0)


FloatArray = NDArray[np.float64]


def unit_vectors(longitudes_rad: FloatArray, latitudes_rad: FloatArray) -> FloatArray:
    cos_lat = np.cos(latitudes_rad)
    return np.column_stack(
        (
            cos_lat * np.cos(longitudes_rad),
            cos_lat * np.sin(longitudes_rad),
            np.sin(latitudes_rad),
        )
    )
