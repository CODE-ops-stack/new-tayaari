import re

text = """Q1. What  are  the  streams  of  charged   particles  ejected  by  the  Sun  into  space   called ?
a) Sunspots
b) Solar wind
c) Solar flares
d) Coronal loops
Correct answer: option b"""

pattern = r"(?s)(.*?)\s*\(?[aA]\)[ )\.](.*?)\s*\(?[bB]\)[ )\.](.*?)\s*\(?[cC]\)[ )\.](.*?)\s*\(?[dD]\)[ )\.](.*?)\s*Correct [Aa]nswer:\s*(?:[Oo]ption\s*)?([a-dA-D])"

match = re.search(pattern, text)
if match:
    print("Match!")
    print("Q:", match.group(1))
    print("A:", match.group(2))
    print("B:", match.group(3))
    print("C:", match.group(4))
    print("D:", match.group(5))
    print("Ans:", match.group(6))
else:
    print("No match!")
