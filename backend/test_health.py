import urllib.request
import json
try:
    with urllib.request.urlopen("http://localhost:8000/health") as response:
        print(response.getcode())
        print(json.loads(response.read().decode()))
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode())
except Exception as e:
    print(e)
