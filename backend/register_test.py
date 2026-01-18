import urllib.request
import json

data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
}

req = urllib.request.Request(
    "http://localhost:8000/auth/register",
    data=json.dumps(data).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.getcode())
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode())
except Exception as e:
    print(e)
