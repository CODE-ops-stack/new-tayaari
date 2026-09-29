from bs4 import BeautifulSoup

try:
    with open("app/build/reports/tests/testDebugUnitTest/classes/com.example.database.RealMigrationTest.html", "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    print(soup.text)
except Exception as e:
    print(e)
