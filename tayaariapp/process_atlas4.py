import json

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

new_sources = registry["sources"]

# Part 06 (Pages 112-131, Back Cover)
new_sources.append({
    "sourceId": "OXFORD_ATLAS_PART06",
    "parentSourceId": "OXFORD_ATLAS_SOURCE_SET",
    "filename": "oxford_atlas_fresh_batch4.pdf",
    "pageCount": 21, # 16 + 5 images
    "edition": "35th Edition",
    "readabilityStatus": "FULLY_READABLE",
    "textStatus": "FULLY_READABLE",
    "mapStatus": "GOOD",
    "extractionMethod": "Vision",
    "partLabel": "Oxford School Atlas (Pages 112-131, Back Cover)",
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

spatial_index["atlas_metadata"]["status"] = "FULL_INGESTION_COMPLETE (Pages Cover-131, Back Cover)"

spatial_index["spatial_coverage"]["MAP_EVIDENCE_GLOBAL_THEMES"].extend([
    "Major Landforms and Forest Cover",
    "Soil and Land Use",
    "Agriculture and Industrial Regions",
    "Minerals, Mineral Fuels, Trade & Economic Dev",
    "Population Density, Urbanization, Religions, Languages",
    "Human Development (Health, Education, Poverty, HDI)",
    "Environmental Concerns (Desertification, Deforestation, Pollution, Biomes at risk)",
    "Plate Tectonics and Natural Hazards",
    "Air Routes and Sea Routes"
])

spatial_index["spatial_coverage"]["REFERENCE_MATERIAL"] = [
    "World Facts & Figures (Flags, Area, Pop, Capital, Language, Currency, GDP)",
    "Statistics - Human Development & Economy (Global Production charts)",
    "Earth-Fact File (Extremes, Waterfalls, Peaks, Rivers, Continental Extremes)",
    "Comparative Heights and Depths (Mountains, Oceans, Lakes)",
    "World Time Zones",
    "Atlas Index"
]

with open(index_path, "w", encoding="utf-8") as f:
    json.dump(spatial_index, f, indent=2)

print("oxford_atlas_spatial_index.json updated.")
