from pathlib import Path
from html.parser import HTMLParser
import json, math, re, xml.etree.ElementTree as ET
site=Path("site")
expected=["force-My.svg","force-Mz.svg","force-N.svg","force-Rz.svg","force-T.svg","force-Vy.svg","force-Vz.svg","force-def.svg","index.html","model-FF.json","model-GF.json","model-TF.json","model-geometry.json","model-isometric.svg","model-plan.svg","model.css","model.js","more.html","projects.html","report.html","staircase.html","studio.html","style.css","truss.svg","visuals.css","visuals.js"]
assert sorted(p.name for p in site.iterdir())==expected
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.links=[]; self.ids=[]
    def handle_data(self,d): self.text.append(d)
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ("href","src") and v: self.links.append(v)
            if k=="id": self.ids.append(v)
for p in site.glob("*.html"):
    h=Document();h.feed(p.read_text())
    assert not re.search(r"\b(?:AI|ChatGPT|OpenAI|Codex|audit|archive|memory wall|version control|revision history|GitHub|our engine|report versus)\b"," ".join(h.text),re.I),p
    for link in h.links:
        if link.startswith("https://"): continue
        name,_,anchor=link.partition("#")
        target=site/name if name else p
        assert target.is_file(),(p,link)
        if anchor:
            dest=Document();dest.feed(target.read_text());assert anchor in dest.ids,(p,link)
for p in site.glob("*.svg"):ET.parse(p)
g=json.loads((site/"model-geometry.json").read_text())
es=sum([json.loads((site/f"model-{st}.json").read_text()) for st in ["GF","FF","TF"]],[])
assert len(g["nodes"])==180 and len(es)==249 and len(g["shells"])==115
assert len({e["id"] for e in es})==165
assert all(len(e["cases"])==2 and all(len(stations)==9 and all(len(s)==10 and all(math.isfinite(v) for v in s) for s in stations) for stations in e["cases"]) for e in es)
assert all(0<=e["i"]<180 and 0<=e["j"]<180 for e in es)
assert all(len(r)==23 and all(len(v)==7 for v in r) for r in g["reactions"])
assert abs(sum(v[3] for v in g["reactions"][0])-7976.1227155)<0.001
assert abs(sum(v[3] for v in g["reactions"][1])-10022.255811)<0.001
report=(site/"report.html").read_text()
for k in ["chapter-1-0","chapter-2-0","chapter-3-0","chapter-4-0","chapter-5-0","chapter-6-0","chapter-6-1","chapter-6-2","chapter-6-3","chapter-6-4","chapter-6-5","chapter-7-0","annex"]:
    assert 'id="'+k+'"' in report
for k in ["N","Vy","Vz","T","My","Mz","def","Ux","Uy","Uz","Rx","Ry","Rz","RMx","RMy","RMz"]:
    assert 'value="'+k+'"' in report
assert "620.747" in report and "94.232" in report
assert "NOT SAFE" in report and "not for construction or procurement" in report
assert "53 / 460" in report and "3.276 m" in report
assert 'id="calculation-workbooks"' in (site/"projects.html").read_text()
for p in [site/"index.html",site/"projects.html",site/"report.html"]:
    assert 'src="visuals.js"' in p.read_text()
assert '@keyframes truss-tour' in (site/"visuals.css").read_text()
print("Structural presentation, model data, figures, quantities and links passed.")
