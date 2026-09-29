import re

html_content = ""
with open("C:\\Users\\harsh\\Downloads\\tayaari\\tayaariapp\\app\\build\\reports\\tests\\testDebugUnitTest\\com.example.database.RealMigrationTest\\testMigration17To19_preservesDataAndAddsColumns.html", "r", encoding="utf-8") as f:
    html_content = f.read()

m = re.search(r"Migration didn't properly handle:\s*([^\(]+).*?Expected:\n(.*?)\n Found:\n(.*?)at androidx", html_content, re.DOTALL)
if m:
    table = m.group(1).strip()
    expected = m.group(2).strip()
    found = m.group(3).strip()
    
    # write to temp files and diff
    with open("expected.txt", "w") as f: f.write(expected)
    with open("found.txt", "w") as f: f.write(found)
    print("Files written. Running diff...")
    import subprocess
    subprocess.run(["diff", "expected.txt", "found.txt"])
else:
    print("Could not parse!")
