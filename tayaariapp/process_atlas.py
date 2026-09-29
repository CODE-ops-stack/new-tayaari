import json
import os
from datetime import datetime

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Keep the old corrupted Oxford Atlas record intact
old_atlas_exists = any("oxford" in str(s.get("filename")).lower() and s.get("readabilityStatus") == "UNRECOVERABLE" for s in registry["sources"])

# Add new Oxford Atlas Parent + Part 1
new_sources = registry["sources"]

new_sources.append({
    "sourceId": "OXFORD_ATLAS_PART01",
    "parentSourceId": "OXFORD_ATLAS_SOURCE_SET",
    "filename": "oxford_atlas_fresh_batch1.pdf",
    "pageCount": 16, # 16 images provided
    "edition": "35th Edition",
    "readabilityStatus": "FULLY_READABLE",
    "textStatus": "FULLY_READABLE",
    "mapStatus": "GOOD",
    "extractionMethod": "Vision",
    "partLabel": "Oxford School Atlas (Pages Cover, Contents, 4-24)",
    "provenance": "Supplied by User as Fresh Source",
    "relationshipToOld": "REPLACEMENT (New uncorrupted scan of 35th Edition)",
    "subject": "Geography",
    "sourceType": "MAPS_AND_SPATIAL"
})

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("source_registry.json updated.")

# Create oxford_atlas_spatial_index.json
spatial_index = {
    "atlas_metadata": {
        "title": "Oxford School Atlas",
        "edition": "35th Edition",
        "publisher": "Oxford University Press",
        "status": "PARTIAL_INGESTION (Batch 1: Pages Cover-24)"
    },
    "spatial_coverage": {
        "THEORY": [
            "History of Cartography", "Remote Sensing and GIS", "Scale Types", 
            "Map Projections (Conical, Cylindrical, Azimuthal)", 
            "Relief Representation (Contours, Hachures, Hill-shading)",
            "Solar System & Earth Interior"
        ],
        "MAP_EVIDENCE_INDIA_PHYSICAL": [
            "Himalayan Ranges & Passes", "Northern Plains", "Peninsular Plateau",
            "Western & Eastern Ghats", "Coastal Plains", "Islands",
            "Major River Basins (Indus, Ganga, Brahmaputra, Peninsular rivers)"
        ],
        "MAP_EVIDENCE_INDIA_POLITICAL": [
            "State Boundaries", "International Frontiers", "Capitals & Major Cities",
            "District Boundaries (in zoomed maps)"
        ]
    }
}

with open("oxford_atlas_spatial_index.json", "w", encoding="utf-8") as f:
    json.dump(spatial_index, f, indent=2)

print("oxford_atlas_spatial_index.json created.")
