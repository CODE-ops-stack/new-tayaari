import urllib.request
import json

# Test manifest from RAW
url = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/topics/manifest.json"
with urllib.request.urlopen(url) as r:
    manifest = json.loads(r.read().decode('utf-8'))
print(f"Live Online Manifest (RAW): version={manifest['version']}, totalQuestions={manifest['totalQuestions']}, totalTopics={manifest['totalTopics']}")

# Test manifest from CDN
cdn_url = "https://cdn.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/topics/manifest.json"
with urllib.request.urlopen(cdn_url) as r:
    cdn_manifest = json.loads(r.read().decode('utf-8'))
print(f"Live Online Manifest (CDN): version={cdn_manifest['version']}, totalQuestions={cdn_manifest['totalQuestions']}, totalTopics={cdn_manifest['totalTopics']}")

# Test metadata from RAW
meta_url = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/metadata.json"
with urllib.request.urlopen(meta_url) as r:
    meta = json.loads(r.read().decode('utf-8'))
print(f"Live Online Metadata: version={meta['version']}, totalQuestions={meta['totalQuestions']}, totalTopics={meta['totalTopics']}, sha256={meta['apkSha256']}")

# Test topic 30 online
url30 = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/topics/topic_30.json"
with urllib.request.urlopen(url30) as r:
    t30 = json.loads(r.read().decode('utf-8'))
print(f"Live Online Topic 30 (RAW): count={len(t30)}, first_stem={t30[0]['stem'][:50]}...")
