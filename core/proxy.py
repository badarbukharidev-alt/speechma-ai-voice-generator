"""
Proxy Manager and Rotation Engine for Speechma TTS.
Provides automatic fetching of public proxies, custom proxy lists, IP header rotation, and health verification.
"""

import json
import logging
import os
import random
import threading
import time
import urllib.request
from pathlib import Path
from typing import List, Optional

from core.config import BASE_DIR

logger = logging.getLogger("speechma.proxy")

PUBLIC_PROXY_SOURCES = [
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
]


class ProxyManager:
    """
    Manages proxy lists, free public proxy discovery, and IP rotation.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProxyManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, custom_proxies: Optional[List[str]] = None):
        if self._initialized:
            if custom_proxies:
                self.add_proxies(custom_proxies)
            return

        self.proxies: List[str] = []
        self.failed_proxies: set = set()
        self.lock = threading.Lock()
        self._last_fetch_time = 0
        self.auto_fetch_enabled = os.getenv("ENABLE_PUBLIC_PROXIES", "1").lower() in ("1", "true", "yes")

        # Load from file if exists (e.g., proxies.txt)
        proxies_file = BASE_DIR / "proxies.txt"
        if proxies_file.exists():
            try:
                with open(proxies_file, "r", encoding="utf-8") as f:
                    file_proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                self.proxies.extend(file_proxies)
                logger.info(f"Loaded {len(file_proxies)} custom proxies from proxies.txt")
            except Exception as e:
                logger.warning(f"Error reading proxies.txt: {e}")

        # Add explicit custom proxies if provided
        if custom_proxies:
            self.proxies.extend(custom_proxies)

        self._initialized = True

    def add_proxies(self, proxy_list: List[str]):
        """Adds a list of proxy strings (ip:port or http://user:pass@ip:port)."""
        with self.lock:
            for p in proxy_list:
                cleaned = p.strip()
                if cleaned and cleaned not in self.proxies:
                    self.proxies.append(cleaned)

    def fetch_public_proxies(self, limit: int = 50) -> int:
        """
        Fetches fresh public proxies from open-source proxy repositories.
        """
        now = time.time()
        # Avoid refetching more than once every 10 minutes
        if now - self._last_fetch_time < 600 and len(self.proxies) > 5:
            return len(self.proxies)

        fetched = []
        for source in PUBLIC_PROXY_SOURCES:
            try:
                req = urllib.request.Request(
                    source,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    lines = resp.read().decode("utf-8", errors="ignore").splitlines()
                    for line in lines:
                        p = line.strip()
                        if p and ":" in p and p not in fetched:
                            fetched.append(p)
                            if len(fetched) >= limit:
                                break
                if len(fetched) >= limit:
                    break
            except Exception as e:
                logger.debug(f"Failed to fetch proxies from {source}: {e}")

        with self.lock:
            for p in fetched:
                if p not in self.proxies:
                    self.proxies.append(p)
            self._last_fetch_time = now

        logger.info(f"ProxyManager: Fetched {len(fetched)} public proxies. Total active: {len(self.proxies)}")
        return len(self.proxies)

    def get_random_proxy(self) -> Optional[dict]:
        """
        Returns a proxies dictionary ready for `requests`, or None if no proxies are configured.
        Format: {'http': 'http://ip:port', 'https': 'http://ip:port'}
        """
        with self.lock:
            # Filter out known permanently failed proxies
            available = [p for p in self.proxies if p not in self.failed_proxies]
            if not available:
                # If all failed, reset failed list to try again
                self.failed_proxies.clear()
                available = list(self.proxies)

        if not available:
            return None

        chosen = random.choice(available)
        if not chosen.startswith("http://") and not chosen.startswith("https://") and not chosen.startswith("socks5://"):
            proxy_url = f"http://{chosen}"
        else:
            proxy_url = chosen

        return {
            "http": proxy_url,
            "https": proxy_url,
        }

    def mark_failed(self, proxy_dict: Optional[dict]):
        """Marks a proxy as failed so it gets deprioritized."""
        if not proxy_dict:
            return
        p_url = proxy_dict.get("http") or proxy_dict.get("https")
        if p_url:
            raw = p_url.replace("http://", "").replace("https://", "").replace("socks5://", "")
            with self.lock:
                self.failed_proxies.add(raw)
                logger.debug(f"Marked proxy as failed: {raw}")

    @staticmethod
    def generate_random_ip() -> str:
        """Generates a random public IPv4 string for X-Forwarded-For rotation."""
        return f"{random.randint(11, 190)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"


# Global default instance
proxy_manager = ProxyManager()
