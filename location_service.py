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

# Known cloud hosting / datacenter cities to reject so server hosting locations are never misattributed to users
DATACENTER_LOCATIONS = {
    "the dalles", "council bluffs", "ashburn", "boardman", "boydton",
    "north charleston", "quincy", "moncks corner", "des moines",
    "mountain view", "omaha", "kansas city", "seattle", "dublin",
    "frankfurt", "zurich", "san jose", "prineville", "reston",
    "sterling", "herndon", "leesburg", "forest city", "columbus", "new albany"
}


def _is_cloud_datacenter(city: str, country: str = "") -> bool:
    """Return True if detected location is a cloud server hosting location (e.g., Streamlit Cloud GCP in The Dalles)."""
    c = (city or "").strip().lower()
    co = (country or "").strip().lower()
    if not c or c == "unknown":
        return True
    if c in DATACENTER_LOCATIONS:
        return True
    if any(k in c for k in ("datacenter", "hosting", "cloud", "aws", "gcp", "azure", "server")):
        return True
    if co in ("united states", "us", "usa") and c in DATACENTER_LOCATIONS:
        return True
    return False


def _is_valid_public_ip(ip: str) -> bool:
    if not ip or not isinstance(ip, str):
        return False
    ip = ip.strip()
    if ip.startswith((
        "127.", "10.", "192.168.", "172.16.", "172.17.", "172.18.",
        "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
        "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.",
        "172.31.", "fc00:", "fe80:", "::1"
    )):
        return False
    return True


def _extract_client_ip() -> Optional[str]:
    """Extract real client IP from Streamlit context or request headers."""
    try:
        import streamlit as st
        # 1. Direct ip_address in st.context
        ip = getattr(st.context, "ip_address", None)
        if ip and _is_valid_public_ip(ip):
            return ip.strip()

        # 2. Check headers
        headers = getattr(st.context, "headers", None) or {}
        for h in ("cf-connecting-ip", "x-real-ip", "x-forwarded-for"):
            val = headers.get(h)
            if val:
                first = val.split(",")[0].strip()
                if _is_valid_public_ip(first):
                    return first
    except Exception:
        pass
    return None


def _try_cloudflare_headers() -> Optional[Dict[str, str]]:
    """Try reading geolocation directly from Cloudflare headers provided by Streamlit Cloud."""
    try:
        import streamlit as st
        headers = getattr(st.context, "headers", None) or {}
        city = headers.get("cf-ipcity")
        country = headers.get("cf-ipcountry")
        region = headers.get("cf-region") or headers.get("cf-region-code") or ""
        if city and not _is_cloud_datacenter(city, country or ""):
            return {
                "city": city,
                "region": region or "West Bengal",
                "country": "India" if country == "IN" else (country or "India"),
                "country_code": (country or "IN").upper(),
                "source": "network_detected",
            }
    except Exception:
        pass
    return None


def detect_location(force_refresh: bool = False) -> Dict[str, str]:
    """
    Auto-detect location using client IP and geolocation when browser GPS is denied/unavailable.
    Guarantees cloud datacenter hosting locations (like The Dalles, US) are rejected.
    Returns: {"city", "region", "country", "country_code", "source": "ip_fallback"}
    """
    # 1. Check Cloudflare reverse-proxy headers (available on Streamlit Cloud)
    cf_loc = _try_cloudflare_headers()
    if cf_loc:
        return cf_loc

    # 3. Detect client IP from Streamlit context
    client_ip = _extract_client_ip()

    services = [
        lambda: _try_ipapi(client_ip),
        lambda: _try_ipinfo(client_ip),
        lambda: _try_ipwhois(client_ip),
    ]

    for service in services:
        try:
            result = service()
            if result and result.get("city") and result.get("city").lower() != "unknown":
                if not _is_cloud_datacenter(result.get("city"), result.get("country", "")):
                    result["source"] = "ip_fallback"
                    logger.info(f"IP Geolocation detected: {result.get('city')}, {result.get('region')}, {result.get('country')}")
                    return result
                else:
                    logger.warning(f"Rejected cloud datacenter location: {result.get('city')}, {result.get('country')}")
        except Exception as e:
            logger.debug(f"IP service failed: {e}")
            continue

    # Default fallback — always clean, authentic Indian regional intelligence
    default = {
        "city": "Kolkata",
        "region": "West Bengal",
        "country": "India",
        "country_code": "IN",
        "source": "default",
    }
    return default


def _try_ipapi(client_ip: Optional[str] = None) -> Optional[Dict[str, str]]:
    url = f"http://ip-api.com/json/{client_ip}" if client_ip else "http://ip-api.com/json/"
    resp = requests.get(url, timeout=4)
    data = resp.json()
    if data.get("status") == "success":
        return {
            "city": data.get("city", ""),
            "region": data.get("regionName", ""),
            "country": data.get("country", "India"),
            "country_code": data.get("countryCode", "IN"),
        }
    return None


def _try_ipinfo(client_ip: Optional[str] = None) -> Optional[Dict[str, str]]:
    url = f"https://ipinfo.io/{client_ip}/json" if client_ip else "https://ipinfo.io/json"
    resp = requests.get(url, timeout=4)
    data = resp.json()
    return {
        "city": data.get("city", ""),
        "region": data.get("region", ""),
        "country": data.get("country", "India"),
        "country_code": data.get("country", "IN"),
    }


def _try_ipwhois(client_ip: Optional[str] = None) -> Optional[Dict[str, str]]:
    url = f"https://ipwhois.app/json/{client_ip}" if client_ip else "https://ipwhois.app/json/"
    resp = requests.get(url, timeout=4)
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

