#!/usr/bin/env python3
"""Smoke test the backend after database recreation.

Run the Flask server first:
    python run.py
"""
import requests

BASE_URL = "http://localhost:5000"

print("Testing backend after database reset...")

print("\n1. Registering new user...")
try:
    data = {
        "email": "newuser@test.com",
        "password": "Test123!",
        "username": "newuser",
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data, timeout=3)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print("   OK: User registered successfully")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as exc:
    print(f"   ERROR: {exc}")

print("\n2. Testing login...")
try:
    data = {"email": "newuser@test.com", "password": "Test123!"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data, timeout=3)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json().get("token", "")
        print(f"   OK: Login successful, token: {token[:20]}...")
    else:
        print(f"   Error: {response.text[:200]}")
except Exception as exc:
    print(f"   ERROR: {exc}")

print("\nBackend fresh database smoke test complete.")
