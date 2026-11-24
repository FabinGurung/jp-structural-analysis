from pathlib import Path
from html.parser import HTMLParser
import re
site=Path("site")
assert {p.name for p in site.iterdir()}=={"index.html","projects.html","report.html","staircase.html","studio.html","more.html","style.css"}
class Visible(HTMLParser):
    def __init__(self):
        super().__init__(); self.words=[]; self.links=[]; self.ids=[]
    def handle_data(self,d): self.words.append(d)
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=="href": self.links.append(v)
            if k=="id": self.ids.append(v)
for p in site.glob("*.html"):
    doc=Visible(); doc.feed(p.read_text())
    visible=" ".join(doc.words)
    assert not re.search(r"\b(?:AI|ChatGPT|OpenAI|Codex|memory wall|version control|revision history|GitHub|commit)\b",visible,re.I),p
    for link in doc.links:
        if link.startswith("https://"): continue
        target,_,anchor=link.partition("#")
        f=site/target if target else p
        assert f.is_file(),link
        if anchor:
            h=Visible(); h.feed(f.read_text()); assert anchor in h.ids,link
report=(site/"report.html").read_text()
expected=["chapter-1-0","chapter-2-0","chapter-3-0","chapter-4-0","chapter-5-0","chapter-6-0","chapter-6-1","chapter-6-2","chapter-6-3","chapter-6-4","chapter-6-5","annex"]
assert all('id="'+k+'"' in report for k in expected)
assert [report.index('id="'+k+'"') for k in expected]==sorted(report.index('id="'+k+'"') for k in expected)
assert report.count("<table>")==11
assert "NOT SAFE" in report and "not an approved structural design" in report
assert "not actual Narayani building results" in report
assert "21.533203" in report and "14.0625" in report
assert "Version Control and Audit" not in report
stair=(site/"staircase.html").read_text()
assert "20.931" in stair and "14.963" in stair and "17.111" in stair and "14.589" in stair
assert len(re.findall(r'<svg viewBox=',stair))==2
assert "NOT SAFE" in (site/"projects.html").read_text()
print("Report presentation checks passed.")
