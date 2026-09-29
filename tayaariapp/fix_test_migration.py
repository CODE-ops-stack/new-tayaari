file = 'app/src/test/java/com/example/database/RealMigrationTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('.addMigrations(AppDatabase.MIGRATION_17_18, AppDatabase.MIGRATION_18_19)', '.addMigrations(AppDatabase.MIGRATION_17_18, AppDatabase.MIGRATION_18_19, AppDatabase.MIGRATION_19_20)')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
