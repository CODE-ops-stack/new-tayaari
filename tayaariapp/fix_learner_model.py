file = 'app/src/main/java/com/example/repository/LearnerModelEngine.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val topics = appDao.getAllTopicsSync()', 'val topics = appDao.getAllTopicsUnwrapped()')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
