import re

text = """Q137. Variations in the length of daytime and nighttime from season to season are dueto
(a) the earth's rotation on its axis
(b) the earth's revolution round the sun in an elliptical manner
(c) latitudinal position of the place
(d) revolution of the earth on a tilted axis\""""

optionsPattern = re.compile(
    r"(?s)(.*?)\s*\(?[aA]\)[ )\.](.*?)\s*\(?[bB]\)[ )\.](.*?)\s*\(?[cC]\)[ )\.](.*?)\s*\(?[dD]\)[ )\.](.*?)(?:\s*Correct [Aa]nswer:|$)"
)

m = optionsPattern.search(text)
if m:
    print("MATCHED!")
    print(m.groups())
else:
    print("NO MATCH")
