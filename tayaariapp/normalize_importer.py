import codecs
with codecs.open('app/src/main/java/com/example/repository/DataImporter.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'val format = matcher.group(3)?.trim() ?: ""' in line:
        insert = '''
                val rawFormat = matcher.group(3)?.trim() ?: ""
                val format = when (val norm = rawFormat.lowercase().replace("-", " ").replace("_", " ")) {
                    "statement", "statement based", "multi statement" -> "Statement-based"
                    "direct fact", "simple", "direct" -> "Direct Fact"
                    "matching", "match the following", "matching pair" -> "Matching"
                    "assertion reason", "assertion" -> "Assertion-Reason"
                    "application", "scenario", "concept application" -> "Application"
                    "" -> "UNCLASSIFIED"
                    else -> "UNCLASSIFIED" // Fallback to avoid guessing
                }
'''
        new_lines.append(insert)
    elif 'val trapType = matcher.group(7)?.trim() ?: ""' in line:
        insert = '''
                val rawTrapType = matcher.group(7)?.trim() ?: ""
                val trapType = when {
                    rawTrapType.isEmpty() || rawTrapType.equals("none", ignoreCase = true) -> ""
                    rawTrapType.lowercase().contains("absolute wording") || rawTrapType.lowercase().contains("extreme wording") -> "ABSOLUTE_WORDING"
                    rawTrapType.lowercase().contains("fact distortion") || rawTrapType.lowercase().contains("fact manipulation") -> "FACT_DISTORTION"
                    rawTrapType.lowercase().contains("familiarity") -> "FAMILIARITY_TRAP"
                    rawTrapType.lowercase().contains("concept mix") || rawTrapType.lowercase().contains("concept blending") -> "CONCEPT_MIX"
                    rawTrapType.lowercase().contains("false correlation") -> "FALSE_CORRELATION"
                    rawTrapType.lowercase().contains("partial truth") -> "PARTIAL_TRUTH"
                    rawTrapType.lowercase().contains("anachronism") || rawTrapType.lowercase().contains("timeline") -> "TIMELINE_MISMATCH"
                    else -> "UNCLASSIFIED_TRAP"
                }
'''
        new_lines.append(insert)
    else:
        new_lines.append(line)

with codecs.open('app/src/main/java/com/example/repository/DataImporter.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
