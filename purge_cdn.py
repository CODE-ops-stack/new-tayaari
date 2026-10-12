import urllib.request
import json

urls = [
    'https://purge.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/metadata.json',
    'https://purge.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/topics/manifest.json',
    'https://purge.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/questions.json'
] + [f'https://purge.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/topics/topic_{t}.json' for t in range(24, 31)]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            name = u.split('/')[-1]
            status = data.get('status')
            print(f"Purged {name}: status={status}")
    except Exception as e:
        print(f"Purge failed for {u}: {e}")
