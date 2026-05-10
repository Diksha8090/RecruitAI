#!/usr/bin/env python3
"""Quick API smoke test.

Run the Flask server first:
    python run.py
"""
import requests

BASE_URL = "http://localhost:5000"

print("Testing AI Resume Screening Backend API...")
print("=" * 60)

print("\n1. Root endpoint")
try:
    response = requests.get(f"{BASE_URL}/", timeout=3)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as exc:
    print(f"   ERROR: {exc}")

print("\n2. User Login")
try:
    data = {"email": "test@example.com", "password": "Password123!"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data, timeout=3)
    print(f"   Status: {response.status_code}")
    result = response.json()

    if response.status_code == 200:
        token = result.get("token", "")
        print("   OK: Login successful")
        print(f"   Token: {token[:20]}...")

        print("\n3. Get Job Postings (with auth)")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/job-postings", headers=headers, timeout=3)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json().get("job_postings", [])
            print(f"   OK: Got {len(jobs)} job postings")
        else:
            print(f"   Error: {response.text[:200]}")
    else:
        print(f"   ERROR: Login failed: {result}")
except Exception as exc:
    print(f"   ERROR: {exc}")

print("\n4. Get Resumes (without auth)")
try:
    response = requests.get(f"{BASE_URL}/api/resumes", timeout=3)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 401]:
        print("   Response received")
    else:
        print(f"   Error: {response.text[:200]}")
except Exception as exc:
    print(f"   ERROR: {exc}")

print("\n" + "=" * 60)
print("Test complete!")
