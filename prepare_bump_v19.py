import json
import os
import shutil
import hashlib
import time

STAGING_DIR = r"c:\Users\harsh\Downloads\tayaari\cloud_data_staging"
TOPICS_DIR = os.path.join(STAGING_DIR, "topics")
MANIFEST_PATH = os.path.join(TOPICS_DIR, "manifest.json")
QUESTIONS_JSON_PATH = os.path.join(STAGING_DIR, "questions.json")
METADATA_PATH = os.path.join(STAGING_DIR, "metadata.json")
BUILD_APK = r"c:\Users\harsh\Downloads\tayaari\tayaariapp\app\build\outputs\apk\debug\app-debug.apk"
STAGING_APK = os.path.join(STAGING_DIR, "app-debug.apk")

# Topic icons for topics 1..30
TOPIC_ICONS = {
    1: "🌌", 2: "🌐", 3: "🗺️", 4: "🌋", 5: "⛰️",
    6: "🌪️", 7: "🌊", 8: "🌿", 9: "🇮🇳", 10: "🏔️",
    11: "🏞️", 12: "🌧️", 13: "🌱", 14: "🐅", 15: "🌾",
    16: "💧", 17: "⛏️", 18: "🏭", 19: "🚆", 20: "👥",
    21: "📈", 22: "🗺️", 23: "📍", 24: "🧠", 25: "📐",
    26: "🗺️", 27: "👥", 28: "🏛️", 29: "⛰️", 30: "🌊"
}

def update_manifest_and_consolidate():
    print("--- 1. Updating manifest.json & questions.json ---")
    all_questions = []
    manifest_topics = []

    for t_id in range(1, 31):
        f_name = f"topic_{t_id}.json"
        f_path = os.path.join(TOPICS_DIR, f_name)
        if not os.path.exists(f_path):
            raise FileNotFoundError(f"Missing topic file: {f_path}")
        
        with open(f_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        count = len(data)
        raw_name = data[0].get("topicName", f"Topic {t_id}")
        icon = TOPIC_ICONS.get(t_id, "📌")
        display_name = f"{icon} {raw_name}" if not raw_name.startswith(icon) else raw_name

        manifest_topics.append({
            "topicId": t_id,
            "topicName": display_name,
            "count": count,
            "file": f_name
        })

        all_questions.extend(data)
        print(f"  Topic {t_id:02d}: {count} questions loaded.")

    total_q = len(all_questions)
    print(f"\nTotal questions accumulated: {total_q}")
    assert total_q == 3942, f"Expected 3942 questions, got {total_q}"

    # Write manifest.json
    manifest = {
        "version": 19,
        "totalQuestions": total_q,
        "totalTopics": len(manifest_topics),
        "topics": manifest_topics
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {MANIFEST_PATH} with {len(manifest_topics)} topics.")

    # Write questions.json
    print(f"Writing consolidated questions.json ({total_q} questions)...")
    with open(QUESTIONS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)
    q_size = os.path.getsize(QUESTIONS_JSON_PATH)
    print(f"Successfully saved {QUESTIONS_JSON_PATH} ({q_size / (1024*1024):.2f} MB).")

    return total_q

def update_apk_and_metadata():
    print("\n--- 2. Updating APK & metadata.json ---")
    if os.path.exists(BUILD_APK):
        print(f"Copying built APK from {BUILD_APK} to {STAGING_APK}...")
        shutil.copy2(BUILD_APK, STAGING_APK)
    else:
        print(f"WARNING: Build APK not found at {BUILD_APK}, using existing staging APK if available.")

    size = os.path.getsize(STAGING_APK)
    with open(STAGING_APK, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest().upper()

    print(f"APK Size: {size} bytes ({size / (1024*1024):.2f} MB)")
    print(f"APK SHA256: {sha256}")

    # Update metadata.json
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta["version"] = 19
    meta["totalQuestions"] = 3942
    meta["totalTopics"] = 30
    meta["apkSha256"] = sha256
    meta["apkSizeBytes"] = size
    meta["updatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    meta["releaseNotes"] = (
        "Version 19.0: Official UPSC Geography Optional Integration & Complete Curriculum Architecture. "
        "Expanded to 3,942 MCQs across 30 Comprehensive Chapters. "
        "Dedicated '🎓 UPSC Geography Optional' track (Chapters 24-30: Perspectives in Human Geography, "
        "Models & Laws, Regional Planning, Cultural Setting, Political Geography, Advanced Geomorphology, "
        "and Advanced Ocean Topography & Climatology). "
        "Every chapter features gradual 3-tier pedagogical leveling (Basic → Medium → Advanced UPSC Ranker), "
        "Amit Khurana Sir's zero-assumption first-principles explanations, Ranker's Memory Locks, "
        "and full distractor dissections. "
        "Approach B: 100% Volatile RAM streaming with strictly 0 persistent questions in SQLite."
    )

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print("Updated metadata.json to version 19.")

    return {
        "version": 19,
        "totalQuestions": 3942,
        "totalTopics": 30,
        "apkSha256": sha256,
        "apkSizeBytes": size,
        "updatedAt": meta["updatedAt"]
    }

if __name__ == "__main__":
    update_manifest_and_consolidate()
    res = update_apk_and_metadata()
    print("\nBump Result Summary:", json.dumps(res, indent=2))
