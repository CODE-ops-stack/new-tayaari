import json

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

new_sources = registry["sources"]

# Part 04 (Pages 78-93)
new_sources.append({
    "sourceId": "OXFORD_ATLAS_PART04",
    "parentSourceId": "OXFORD_ATLAS_SOURCE_SET",
    "filename": "oxford_atlas_fresh_batch3a.pdf",
    "pageCount": 16,
    "edition": "35th Edition",
    "readabilityStatus": "FULLY_READABLE",
    "textStatus": "FULLY_READABLE",
    "mapStatus": "GOOD",
    "extractionMethod": "Vision",
    "partLabel": "Oxford School Atlas (Pages 78-93)",
    "provenance": "Supplied by User as Fresh Source",
    "relationshipToOld": "REPLACEMENT (New uncorrupted scan of 35th Edition)",
    "subject": "Geography",
    "sourceType": "MAPS_AND_SPATIAL"
})

# Part 05 (Pages 94-111)
new_sources.append({
    "sourceId": "OXFORD_ATLAS_PART05",
    "parentSourceId": "OXFORD_ATLAS_SOURCE_SET",
    "filename": "oxford_atlas_fresh_batch3b.pdf",
    "pageCount": 16,
    "edition": "35th Edition",
    "readabilityStatus": "FULLY_READABLE",
    "textStatus": "FULLY_READABLE",
    "mapStatus": "GOOD",
    "extractionMethod": "Vision",
    "partLabel": "Oxford School Atlas (Pages 94-111)",
    "provenance": "Supplied by User as Fresh Source",
    "relationshipToOld": "REPLACEMENT (New uncorrupted scan of 35th Edition)",
    "subject": "Geography",
    "sourceType": "MAPS_AND_SPATIAL"
})

registry["sources"] = new_sources

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("source_registry.json updated.")

# Update oxford_atlas_spatial_index.json
index_path = "oxford_atlas_spatial_index.json"
with open(index_path, "r", encoding="utf-8") as f:
    spatial_index = json.load(f)

spatial_index["atlas_metadata"]["status"] = "PARTIAL_INGESTION (Batch 1-3: Pages Cover-111)"

spatial_index["spatial_coverage"]["MAP_EVIDENCE_WORLD_REGIONS"] = [
    "Europe (Physical, Political, Climate, British Isles, Central Europe)",
    "Africa (Physical, Political, Climate, Southern Africa)",
    "North America (Physical, Political, Climate, USA, Alaska)",
    "South America (Physical, Political, Climate, Brazil)",
    "Oceania (Physical, Political, Climate)"
]

spatial_index["spatial_coverage"]["MAP_EVIDENCE_GLOBAL_THEMES"] = [
    "Oceans (Pacific, Indian, Atlantic, Arctic, Southern/Antarctica)",
    "World Physical (Mountains, Basins, Trenches)",
    "World Political (Countries, Capitals)",
    "Global Mean Temperature (January, July)",
    "Global Pressure & Winds (January, July)",
    "Annual Rainfall & Major Ocean Currents (Warm/Cold)",
    "Climatic Regions (Koppen's Classification) & Watersheds"
]

with open(index_path, "w", encoding="utf-8") as f:
    json.dump(spatial_index, f, indent=2)

print("oxford_atlas_spatial_index.json updated.")
