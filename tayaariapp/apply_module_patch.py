import re
import os

# 1. Update Entities.kt
entities_path = "app/src/main/java/com/example/database/Entities.kt"
with open(entities_path, "r", encoding="utf-8") as f:
    entities_code = f.read()

entities_code = entities_code.replace(
    "val source: String",
    "val source: String,\n    val module: String = \"Miscellaneous Topics\""
)
with open(entities_path, "w", encoding="utf-8") as f:
    f.write(entities_code)


# 2. Update AppDatabase.kt
db_path = "app/src/main/java/com/example/database/AppDatabase.kt"
with open(db_path, "r", encoding="utf-8") as f:
    db_code = f.read()

db_code = db_code.replace("version = 20", "version = 21")

migration_20_21 = """        val MIGRATION_20_21 = object : Migration(20, 21) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE topics ADD COLUMN module TEXT NOT NULL DEFAULT 'Miscellaneous Topics'")
            }
        }
"""
db_code = db_code.replace("        val MIGRATION_19_20", migration_20_21 + "        val MIGRATION_19_20")
db_code = db_code.replace(".addMigrations(MIGRATION_17_18, MIGRATION_18_19, MIGRATION_19_20)", ".addMigrations(MIGRATION_17_18, MIGRATION_18_19, MIGRATION_19_20, MIGRATION_20_21)")

with open(db_path, "w", encoding="utf-8") as f:
    f.write(db_code)


# 3. Update DataImporter.kt
importer_path = "app/src/main/java/com/example/repository/DataImporter.kt"
with open(importer_path, "r", encoding="utf-8") as f:
    importer_code = f.read()

get_module_fun = """
    private fun getTopicModule(topicName: String): String {
        val normalized = topicName.substringAfter(". ").trim()
        return when {
            normalized in listOf("The Earth in the Solar System", "Globe: Latitudes and Longitudes", "Motions of the Earth", "Major Domains of the Earth", "Major Landforms of the Earth", "Interior of the Earth", "Geomorphic Processes", "Landforms and their Evolution", "Composition and Structure of Atmosphere", "Solar Radiation, Heat Balance and Temperature", "Atmospheric Circulation and Weather Systems", "Water in the Atmosphere", "World Climate and Climate Change", "Water (Oceans)", "Movements of Ocean Water", "Biodiversity and Conservation", "Natural Hazards and Disasters") -> "Physical Geography"
            normalized in listOf("Our Country - India", "India - Location", "Structure and Physiography", "Drainage System", "Climate", "Natural Vegetation", "Transport and Communication (India)", "Land Resources and Agriculture", "Water Resources", "Mineral and Energy Resources") -> "Indian Geography"
            normalized in listOf("Transport and Communication", "Population: Distribution, Density, Growth and Composition") -> "Human & Economic Geography"
            else -> "Miscellaneous Topics"
        }
    }
"""

importer_code = importer_code.replace(
    "topics.add(Topic(tNum, \"$tNum. $tName\", \"Mapped Source\"))",
    "topics.add(Topic(tNum, \"$tNum. $tName\", \"Mapped Source\", getTopicModule(tName)))"
)

if "private fun getTopicModule" not in importer_code:
    importer_code = importer_code.replace("suspend fun importFromMarkdown", get_module_fun + "\n    suspend fun importFromMarkdown")

with open(importer_path, "w", encoding="utf-8") as f:
    f.write(importer_code)


# 4. Update TopicSelectionScreen.kt
topic_path = "app/src/main/java/com/example/ui/screens/TopicSelectionScreen.kt"
with open(topic_path, "r", encoding="utf-8") as f:
    topic_code = f.read()

# Remove the hardcoded getTopicModule function
topic_code = re.sub(r"fun getTopicModule.*?}\s*@OptIn", "@OptIn", topic_code, flags=re.DOTALL)

# Update the grouping
topic_code = topic_code.replace("topics.groupBy { getTopicModule(it.topic.name) }", "topics.groupBy { it.topic.module }")

with open(topic_path, "w", encoding="utf-8") as f:
    f.write(topic_code)

print("Applied data-driven module mapping!")
