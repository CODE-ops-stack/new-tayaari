import json

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

new_sources = registry["sources"]

# Part 02 (Pages 46-61)
new_sources.append({
    "sourceId": "OXFORD_ATLAS_PART02",
    "parentSourceId": "OXFORD_ATLAS_SOURCE_SET",
    "filename": "oxford_atlas_fresh_batch2a.pdf",
    "pageCount": 16,
    "edition": "35th Edition",
    "readabilityStatus": "FULLY_READABLE",
    "textStatus": "FULLY_READABLE",
    "mapStatus": "GOOD",
    "extractionMethod": "Vision",
    "partLabel": "Oxford School Atlas (Pages 46-61)",
    "provenance": "Supplied by User as Fresh Source",
    "relationshipToOld": "REPLACEMENT (New uncorrupted scan of 35th Edition)",
    "subject": "Geography",
    "sourceType": "MAPS_AND_SPATIAL"
})

# Part 03 (Pages 62-77)
new_sources.append({
    "sourceId": "OXFORD_ATLAS_PART03",
    "parentSourceId": "OXFORD_ATLAS_SOURCE_SET",
    "filename": "oxford_atlas_fresh_batch2b.pdf",
    "pageCount": 16,
    "edition": "35th Edition",
    "readabilityStatus": "FULLY_READABLE",
    "textStatus": "FULLY_READABLE",
    "mapStatus": "GOOD",
    "extractionMethod": "Vision",
    "partLabel": "Oxford School Atlas (Pages 62-77)",
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

spatial_index["atlas_metadata"]["status"] = "PARTIAL_INGESTION (Batch 1-2: Pages Cover-77)"

spatial_index["spatial_coverage"]["MAP_EVIDENCE_INDIA_THEMATIC"] = [
    "Metallic & Non-Metallic Minerals", "Energy & Power Projects", 
    "Industrial Regions", "Roads, Railways, Waterways, Airways",
    "Population Demographics (Density, Growth, Sex Ratio, Urbanization)",
    "Health & Socio-Economic Indicators", "Religions & Languages",
    "Tourism & World Heritage Sites", "Cultural Heritage (Dances/Festivals)",
    "Environmental Concerns (Pollution, Degradation, Endangered Species)",
    "Natural Hazards (Earthquakes, Cyclones, Droughts, Floods)"
]

spatial_index["spatial_coverage"]["MAP_EVIDENCE_ASIA"] = [
    "Asia Physical (Ranges, Basins, Rivers, Plateaus)", 
    "Asia Political (Countries, Capitals)",
    "Asia Climate & Economy", 
    "SAARC Region", 
    "East Asia (China, Japan, Koreas, Taiwan, Mongolia)", 
    "South-East Asia"
]

with open(index_path, "w", encoding="utf-8") as f:
    json.dump(spatial_index, f, indent=2)

print("oxford_atlas_spatial_index.json updated.")
