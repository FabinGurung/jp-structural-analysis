from pathlib import Path
from html.parser import HTMLParser
import re
site=Path("site")
assert {p.name for p in site.iterdir()}=={"index.html","projects.html","report.html","studio.html","more.html","style.css"}
class Visible(HTMLParser):
    def __init__(self):
        super().__init__(); self.words=[]; self.links=[]
    def handle_data(self,d): self.words.append(d)
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=="href": self.links.append(v)
for p in site.glob("*.html"):
    doc=Visible(); doc.feed(p.read_text())
    visible=" ".join(doc.words)
    assert not re.search(r"\b(?:AI|ChatGPT|OpenAI|Codex|automation|workflow|audit|memory wall|version control|archive|OpenSees|synthetic|GitHub|commit|revision history)\b",visible,re.I),p
    for link in doc.links:
        if not link.startswith(("https://","#")): assert (site/link.split("#")[0]).is_file(),link
report=(site/"report.html").read_text()
assert "Engineering review required" in report
assert "not approved construction values" in report
assert "20.931" in report and "14.963" in report
assert "17.111" in report and "14.589" in report
assert "Conditional AB and BC line models" in report
assert "NOT SAFE" in (site/"projects.html").read_text()
assert "Version Control and Audit" not in report
assert len(re.findall(r'<svg viewBox=',report))==2
print("Presentation and engineering review checks passed.")
