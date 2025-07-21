from .base import *
import socket

DEBUG = True

def get_local_ip():
    """로컬 IP 자동 감지"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
    get_local_ip(),  # 자동 수집된 로컬 IP
]