#!/usr/bin/env python3
"""
Health check script to verify all services are running.
"""

import requests
import time
import sys

def check_service(url, service_name):
    """Check if a service is responding."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} is healthy")
            return True
        else:
            print(f"❌ {service_name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {service_name} is not responding: {e}")
        return False

def main():
    """Check all services."""
    services = [
        ("http://127.0.0.1:9000/health", "API Server"),
        ("http://127.0.0.1:9090", "UI Server"),
        ("http://127.0.0.1:8080", "Analytics Server")
    ]
    
    # Check each service with retries
    all_healthy = True
    for url, name in services:
        retries = 3
        for attempt in range(retries):
            if check_service(url, name):
                break
            elif attempt < retries - 1:
                print(f"⚠️  Retrying {name} in 5 seconds... (attempt {attempt + 1}/{retries})")
                time.sleep(5)
            else:
                print(f"❌ {name} failed after {retries} attempts")
                all_healthy = False
    
    if all_healthy:
        print("🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("❌ Some services are not healthy!")
        sys.exit(1)

if __name__ == "__main__":
    main() 