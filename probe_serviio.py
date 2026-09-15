import urllib.request, urllib.error, re, json, os

base = 'http://192.168.1.5:23423'

# First, try to GET the export endpoint to understand the .sob format
print("--- Getting current .sob format from server ---")
try:
    req = urllib.request.Request(base + '/rest/import-export/online', method='GET')
    req.add_header('Accept', 'application/json')
    r = urllib.request.urlopen(req, timeout=10)
    data = r.read()
    print(f"Status: {r.status}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Size: {len(data)} bytes")
    
    # Try to decode as text
    try:
        text = data.decode('utf-8')
        print(f"\nFirst 2000 chars:")
        print(text[:2000])
    except:
        print("Could not decode as text")
    
    # Save the sample .sob file
    with open(r'F:\bkp\Documents\Claude\opencode\Iptv-Brasil-2026-master\filtered\sample.sob', 'wb') as f:
        f.write(data)
    print(f"\nSaved sample.sob ({len(data)} bytes)")
    
except urllib.error.HTTPError as e:
    try:
        body = e.read()
        print(f"Error: {e.code}")
        print(f"Body: {body[:500]}")
    except:
        print(f"Error: {e.code}")
except Exception as e:
    print(f"Error: {e}")

# Also check if we can get the current repository configuration
print("\n--- Trying to get repository data ---")
try:
    req = urllib.request.Request(base + '/rest/action', method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Origin', base)
    req.add_header('Referer', 'http://192.168.1.5:23423/console/#/app/library/online')
    req.data = json.dumps({'name': 'getOnlineRepositories', 'parameter': []}).encode()
    r = urllib.request.urlopen(req, timeout=10)
    body = r.read().decode('utf-8', errors='replace')[:1000]
    print(f"Result: {body[:800]}")
except Exception as e:
    print(f"Error: {e}")
