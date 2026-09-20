"""
Location Service — Browser GPS & IP-Aware Geolocation
───────────────────────────────────────────────────────
Provides location-aware local news discovery:
  • Browser HTML5 Geolocation reverse geocoding
  • IP-based fallback if GPS is denied or unavailable
  • Scoped news query generation (Local, National, Global)
  • Does NOT restrict global news discovery or arbitrary search
"""

import logging
import requests
from typing import Dict, Optional, Any

logger = logging.getLogger("news_rag.location")

_ip_location_cache: Optional[Dict[str, str]] = None


def reverse_geocode(lat: float, lon: float) -> Dict[str, str]:
    """
    Reverse geocode GPS coordinates (latitude, longitude) into City, State, Country.
    Uses free BigDataCloud Client Reverse Geocode API and Nominatim.
    """
    # 1. Try BigDataCloud (fast, free, no key required)
    try:
        url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city") or data.get("locality") or data.get("principalSubdivision") or ""
            region = data.get("principalSubdivision") or ""
            country = data.get("countryName") or "India"
            country_code = data.get("countryCode") or "IN"
            if city or region:
                logger.info(f"📍 GPS Reverse geocoded: {city}, {region}, {country}")
                return {
                    "city": city or region,
                    "region": region,
                    "country": country,
                    "country_code": country_code.upper(),
                    "source": "browser_gps",
                    "lat": lat,
                    "lon": lon,
                }
    except Exception as e:
        logger.warning(f"BigDataCloud reverse geocode failed: {e}")

    # 2. Try OpenStreetMap Nominatim fallback
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        headers = {"User-Agent": "TrikonDrishti-NewsIntelligence/2.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            addr = data.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("state_district") or addr.get("county") or ""
            region = addr.get("state") or ""
            country = addr.get("country") or "India"
            country_code = addr.get("country_code", "in").upper()
            return {
                "city": city or region,
                "region": region,
                "country": country,
                "country_code": country_code,
                "source": "browser_gps",
                "lat": lat,
                "lon": lon,
            }
    except Exception as e:
        logger.warning(f"Nominatim reverse geocode failed: {e}")

    # Fallback to IP detection if reverse geocode failed
    return detect_location()


import json
from pathlib import Path

LOC_CACHE_FILE = Path(__file__).parent / "last_location.json"


def detect_location(force_refresh: bool = False) -> Dict[str, str]:
    """
    Auto-detect location using free IP geolocation when browser GPS is denied/unavailable.
    Returns: {"city", "region", "country", "country_code", "source": "ip_fallback"}
    """
    global _ip_location_cache
    if not force_refresh and _ip_location_cache is not None:
        return _ip_location_cache

    # Check disk cache first for instantaneous startup
    if not force_refresh and LOC_CACHE_FILE.exists():
        try:
            with open(LOC_CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if cached.get("city"):
                    _ip_location_cache = cached
                    return cached
        except Exception:
            pass

    services = [
        _try_ipapi,
        _try_ipinfo,
        _try_ipwhois,
    ]

    for service in services:
        try:
            result = service()
            if result and result.get("city") and result.get("city").lower() != "unknown":
                result["source"] = "ip_fallback"
                _ip_location_cache = result
                try:
                    with open(LOC_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2)
                except Exception:
                    pass
                logger.info(f"IP Geolocation detected: {result.get('city')}, {result.get('region')}, {result.get('country')}")
                return result
        except Exception as e:
            logger.debug(f"IP service failed: {e}")
            continue

    # Default fallback
    default = {
        "city": "Kolkata",
        "region": "West Bengal",
        "country": "India",
        "country_code": "IN",
        "source": "default",
    }
    _ip_location_cache = default
    try:
        with open(LOC_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
    except Exception:
        pass
    return default



def _try_ipapi() -> Optional[Dict[str, str]]:
    resp = requests.get("http://ip-api.com/json/", timeout=4)
    data = resp.json()
    if data.get("status") == "success":
        return {
            "city": data.get("city", ""),
            "region": data.get("regionName", ""),
            "country": data.get("country", "India"),
            "country_code": data.get("countryCode", "IN"),
        }
    return None


def _try_ipinfo() -> Optional[Dict[str, str]]:
    resp = requests.get("https://ipinfo.io/json", timeout=4)
    data = resp.json()
    return {
        "city": data.get("city", ""),
        "region": data.get("region", ""),
        "country": data.get("country", "India"),
        "country_code": data.get("country", "IN"),
    }


def _try_ipwhois() -> Optional[Dict[str, str]]:
    resp = requests.get("https://ipwhois.app/json/", timeout=4)
    data = resp.json()
    return {
        "city": data.get("city", ""),
        "region": data.get("region", ""),
        "country": data.get("country", "India"),
        "country_code": data.get("country_code", "IN"),
    }


def get_location_display(loc: Dict[str, str]) -> str:
    """Format location into a concise display label."""
    city = loc.get("city", "").strip()
    region = loc.get("region", "").strip()
    country = loc.get("country", "").strip()

    parts = []
    if city and city.lower() != "unknown":
        parts.append(city)
    if region and region.lower() != "unknown" and region != city:
        parts.append(region)
    if country and country.lower() != "unknown":
        parts.append(country)

    return ", ".join(parts) if parts else "Global News Mode"


def get_location_source_badge(loc: Dict[str, str]) -> Dict[str, str]:
    """Return badge text and CSS class based on location source."""
    source = loc.get("source", "default")
    if source == "browser_gps":
        return {"text": "GPS Verified", "class": "badge-gps", "icon": ""}
    elif source == "manual":
        return {"text": "Custom Region", "class": "badge-manual", "icon": ""}
    elif source == "ip_fallback":
        return {"text": "Network Auto-Detect", "class": "badge-ip", "icon": ""}
    else:
        return {"text": "Default Region", "class": "badge-def", "icon": ""}

