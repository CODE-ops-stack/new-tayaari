import collections

with open('file_list.txt', 'w') as f:
    pass

data = """
2 bytes - /app/applet/assets/.aistudio/.gitignore
7 bytes - /app/applet/app/.gitignore
54 bytes - /app/applet/package.json
76 bytes - /app/applet/app/src/main/res/values/strings.xml
155 bytes - /app/applet/app/src/main/res/values/themes.xml
210 bytes - /app/applet/metadata.json
253 bytes - /app/applet/.gitignore
325 bytes - /app/applet/app/src/test/java/com/example/ExampleUnitTest.kt
344 bytes - /app/applet/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml
344 bytes - /app/applet/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml
347 bytes - /app/applet/script.py
379 bytes - /app/applet/app/src/main/res/values/colors.xml
381 bytes - /app/applet/.env.example
405 bytes - /app/applet/build.gradle.kts
455 bytes - /app/applet/fix_repo.py
479 bytes - /app/applet/app/src/main/res/xml/backup_rules.xml
504 bytes - /app/applet/source-material/exam-complexity-profiles.md
552 bytes - /app/applet/app/src/main/res/xml/data_extraction_rules.xml
553 bytes - /app/applet/settings.gradle.kts
562 bytes - /app/applet/app/src/main/java/com/example/ui/theme/Color.kt
566 bytes - /app/applet/app/src/test/java/com/example/MainActivityTest.kt
570 bytes - /app/applet/app/src/test/java/com/example/DatabaseInitializationTest.kt
591 bytes - /app/applet/app/src/test/java/com/example/ExampleRobolectricTest.kt
607 bytes - /app/applet/app/applet/source-material_new/exam-complexity-profiles.md
630 bytes - /app/applet/app/src/androidTest/java/com/example/ExampleInstrumentedTest.kt
751 bytes - /app/applet/app/proguard-rules.pro
780 bytes - /app/applet/extract.py
795 bytes - /app/applet/generate_report.py
862 bytes - /app/applet/app/applet/extract.py
870 bytes - /app/applet/preserve_ssc.py
994 bytes - /app/applet/app/src/main/java/com/example/ui/theme/Type.kt
1077 bytes - /app/applet/app/src/main/AndroidManifest.xml
1093 bytes - /app/applet/app/src/main/java/com/example/database/AppDatabase.kt
1159 bytes - /app/applet/app/src/test/java/com/example/ViewModelInitializationTest.kt
1174 bytes - /app/applet/app/applet/source-material_new/geography-syllabus-gs.md
1413 bytes - /app/applet/app/src/main/java/com/example/database/Entities.kt
1485 bytes - /app/applet/app/src/main/res/mipmap-mdpi/ic_launcher.webp
1517 bytes - /app/applet/gradle.properties
1597 bytes - /app/applet/topics.txt
1703 bytes - /app/applet/app/src/main/res/drawable/ic_launcher_foreground.xml
1879 bytes - /app/applet/app/src/test/java/com/example/database/RegexTest.kt
1953 bytes - /app/applet/app/applet/source-material_new/design-system.md
1953 bytes - /app/applet/source-material/_backup/design-system.md_20260805065828
1953 bytes - /app/applet/source-material/design-system.md
2015 bytes - /app/applet/source-material/geography-syllabus-gs.md
2021 bytes - /app/applet/app/src/test/java/com/example/database/DataImporterTest.kt
2096 bytes - /app/applet/app/src/main/res/mipmap-hdpi/ic_launcher.webp
2361 bytes - /app/applet/app/src/main/java/com/example/database/Daos.kt
2428 bytes - /app/applet/app/src/main/java/com/example/ui/theme/Theme.kt
2457 bytes - /app/applet/app/src/main/java/com/example/repository/LocalRepository.kt
2479 bytes - /app/applet/upsc_report.txt
2525 bytes - /app/applet/source-material/_backup/examiner-pattern-guide.md_20260805065828
2525 bytes - /app/applet/source-material/examiner-pattern-guide.md
2564 bytes - /app/applet/app/src/main/java/com/example/MainActivity.kt
2634 bytes - /app/applet/app/src/main/res/mipmap-mdpi/ic_launcher_round.webp
2666 bytes - /app/applet/debug.keystore
2854 bytes - /app/applet/app/src/main/res/mipmap-xhdpi/ic_launcher.webp
2868 bytes - /app/applet/app/src/test/screenshots/greeting.png
2948 bytes - /app/applet/app/src/main/java/com/example/ui/screens/TrapDashboardScreen.kt
3142 bytes - /app/applet/source-material/pyq-analysis-prelims.md
3482 bytes - /app/applet/app/src/main/java/com/example/model/TestModels.kt
3556 bytes - /app/applet/debug.keystore.base64
4125 bytes - /app/applet/rewrite.py
4184 bytes - /app/applet/source-material/_backup/file-categories.md_20260805065828
4184 bytes - /app/applet/source-material/file-categories.md
4305 bytes - /app/applet/app/src/main/res/mipmap-hdpi/ic_launcher_round.webp
4360 bytes - /app/applet/app/src/main/res/mipmap-xxhdpi/ic_launcher.webp
4453 bytes - /app/applet/fix_upsc2.py
4586 bytes - /app/applet/app/applet/fix_upsc.py
4636 bytes - /app/applet/classified_report.json
4821 bytes - /app/applet/app/applet/fix_upsc2.py
5006 bytes - /app/applet/app/src/main/java/com/example/repository/DataImporter.kt
5068 bytes - /app/applet/app/build.gradle.kts
5606 bytes - /app/applet/app/src/main/res/drawable/ic_launcher_background.xml
5743 bytes - /app/applet/app/src/main/res/mipmap-xxxhdpi/ic_launcher.webp
5934 bytes - /app/applet/app/src/main/res/mipmap-xhdpi/ic_launcher_round.webp
6573 bytes - /app/applet/app/src/main/java/com/example/viewmodel/PracticeViewModel.kt
7184 bytes - /app/applet/package-lock.json
7472 bytes - /app/applet/gradle/libs.versions.toml
8108 bytes - /app/applet/app/src/main/java/com/example/repository/GeminiRepository.kt
8887 bytes - /app/applet/app/src/main/res/mipmap-xxhdpi/ic_launcher_round.webp
8964 bytes - /app/applet/source-material/geography-syllabus.md
9721 bytes - /app/applet/classify.py
11709 bytes - /app/applet/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.webp
14096 bytes - /app/applet/app/src/main/java/com/example/ui/screens/PracticeScreen.kt
17988 bytes - /app/applet/source-material/_backup/gap_report.txt_20260805065828
17988 bytes - /app/applet/source-material/gap_report.txt
24868 bytes - /app/applet/source-material/_backup/consolidated_grounding.md_20260805065828
25763 bytes - /app/applet/source-material/consolidated_grounding.md
71503 bytes - /app/applet/upsc_data.json
78176 bytes - /app/applet/upsc_extracted.json
87662 bytes - /app/applet/classified_questions.json
295346 bytes - /app/applet/src_data.json
1203814 bytes - /app/applet/source-material/question.pdf
1380903 bytes - /app/applet/source-material/Geomagnetism & Geomagnetic Reversal - UPSC - UPSC Notes » LotusArise IAS.pdf
1785934 bytes - /app/applet/source-material/geography_questions_in_UPSC_Prelims_05c936a1aa(1).pdf
3384356 bytes - /app/applet/source-material/newGeography.pdf
3572352 bytes - /app/applet/source-material/Earth’s Magnetic Field, Dynamo theory, Magnetosphere - PMF IAS (1).pdf
3580706 bytes - /app/applet/source-material/fatman Geography 2nd Edition_Part3.pdf
3589021 bytes - /app/applet/source-material/fatman Geography 2nd Edition_Part4.pdf
4436871 bytes - /app/applet/source-material/Practical Work in Geography Part 2.pdf
5059481 bytes - /app/applet/source-material/NCERT-Class-9-Geography-1.pdf
6127693 bytes - /app/applet/source-material/India Physical Environment (Class XI) 2.pdf
6268672 bytes - /app/applet/source-material/Fundamental of Physical Geography (Class XI) 2.pdf
6567166 bytes - /app/applet/source-material/India People and Economy (Class XII).pdf
7343326 bytes - /app/applet/source-material/Practical Work in Geography Part 1.pdf
8476189 bytes - /app/applet/source-material/NCERT-Class-10-Geography.pdf
11475969 bytes - /app/applet/source-material/Environment (Apr 2025 - Nov 2025)_compressed.pdf
13334563 bytes - /app/applet/source-material/fatman Geography 2nd Edition_Part5.pdf
13741852 bytes - /app/applet/source-material/fatman Geography 2nd Edition_Part2_new 2.pdf
14069524 bytes - /app/applet/source-material/Fundamentals of Human Geography (Class XII) 1.pdf
14406104 bytes - /app/applet/source-material/fatman Geography 2nd Edition_Part1 new.pdf
15380205 bytes - /app/applet/source-material/social science class 8.pdf
16366821 bytes - /app/applet/source-material/GEOGRAPHY 4.0 ENGLISH pdf (2)_new 21.pdf
16786993 bytes - /app/applet/source-material/VisionIAS Research And Analysis January 2025 Geography (10 Years UPSC PYQ Trend Analysis) (1)_compressed (1).pdf
17240182 bytes - /app/applet/source-material/GEOGRAPHY 4.0 ENGLISH pdf (2)__new2.pdf
17923023 bytes - /app/applet/source-material/Geogrophy.pdf
19029293 bytes - /app/applet/source-material/Copy of our environmemnt class 7 - .pdf
24597714 bytes - /app/applet/source-material/oxford-student-atlas-35-edition-freeupscmaterials.org__compressed.pdf
24628882 bytes - /app/applet/source-material/ccab2-geography.pdf
"""

directories = collections.defaultdict(list)
for line in data.strip().split('\n'):
    size, _, path = line.partition(' - ')
    path = path.replace('/app/applet/', '')
    if '/' in path:
        folder = path[:path.rfind('/')]
        file = path[path.rfind('/')+1:]
    else:
        folder = "Root"
        file = path
    directories[folder].append(f"- `{file}`: {size}")

with open('/app/applet/formatted_list.md', 'w') as f:
    for folder, files in sorted(directories.items()):
        f.write(f"### {folder}\n")
        f.write('\n'.join(files) + '\n\n')
