import re
with open("/app/applet/classified_questions.json") as f:
    orig = __import__('json').load(f)
    print("Blocks:", len(orig))
