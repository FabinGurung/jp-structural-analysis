"""Chapter 6 beam flexure+shear report for actual source-backed R6.23 actions.

Visualization only; all numerical operations belong in beam_design.py.
"""
from html import escape
from r6p30.beam_design import SCHEMA, CODE_URL

def e(value):
    return escape(str(value),quote=True)

def fmt(value,places=3):
    return "—" if value is None else format(float(value),f",.{places}f")

def table(headers,rows):
    head="<thead><tr>"+"".join("<th>"+e(h)+"</th>" for h in headers)+"</tr></thead>"
    body="".join("<tr>"+"".join("<td>"+e(c)+"</td>" for c in row)+"</tr>" for row in rows)
    return '<div class="scroll"><table>'+head+"<tbody>"+body+"</tbody></table></div>"

def render_beam_chapter(beam):
    if beam["schema"]!=SCHEMA or beam["professional_engineering_approval"]:
        raise ValueError("R6.31 requires a synthetic, non-approved calculation record")
    m=beam["governing_bending_row"]
    v=beam["governing_vertical_shear_row"]
    b=beam["assumed_section"]
    count=beam["rows_count"]
    summary=table(("Item","Calculated result","Provenance / caveat"),[
      ("Model coverage",f'{beam["beam_count"]} beams × 2 ends × 2 U± combinations × 2 diaphragm modes',
       f'{count} signed end checks'),
      ("Assumed section",f'{fmt(b["b_mm"])} × {fmt(b["D_mm"])} mm; d={fmt(b["d_mm"])} mm',
       "Synthetic, not original Narayani geometry"),
      ("Longitudinal bars",f'{b["longitudinal_bars_each_face"]} Ø{fmt(b["longitudinal_bar_diameter_mm"])} EACH face',
       "Assumed top and bottom; continuity/anchorage not verified"),
      ("Stirrups",f'{b["stirrup_legs"]} legs Ø{fmt(b["stirrup_diameter_mm"])} @ {fmt(b["stirrup_spacing_mm"])} mm',
       "Vertical ties; Fe415 effective shear cap"),
      ("Governing signed My",fmt(m["flexure"]["Mu_abs_kNm"])+" kN·m",
       m["mode"]+" / "+m["case"]+" / "+m["member"]+" / "+m["end"]),
      ("Governing As required / As provided",
       fmt(m["flexure"]["As_required_including_min_mm2"])+" / "+fmt(m["flexure"]["As_provided_tension_mm2"])+" mm²",
       m["flexure"]["status"]),
      ("Governing signed Vz",fmt(v["shear"]["Vu_abs_kN"])+" kN",
       v["mode"]+" / "+v["case"]+" / "+v["member"]+" / "+v["end"]),
      ("Governing τv / τc / τc,max",
       " / ".join(fmt(v["shear"][name]) for name in ("tau_v_MPa","tau_c_MPa","tau_cmax_MPa"))+" MPa",
       v["shear"]["status"]),
      ("Max permissible stirrup spacing from governing Vz",
       fmt(v["shear"]["stirrup_s_upper_bound_mm"])+" mm",
       "Minimum steel, 0.75d, 300mm and required Vus all included"),
      ("Isolated flexure section screens",
       str(beam["isolated_screen_flexure_ok_count"])+"/"+str(count),
       "Do not equate a section screen with full structure acceptance"),
      ("Isolated shear section screens",
       str(beam["isolated_screen_shear_ok_count"])+"/"+str(count),
       "Does not design torsion or other-axis shear")
    ])
    all_rows=[]
    for q in beam["all_qualifying_beam_end_case_rows"]:
        f=q["flexure"];s=q["shear"];act=q["signed_local_actions"]
        all_rows.append((q["mode"].replace("_"," "),q["case"],q["member"],q["end"],
         fmt(act["My"]),fmt(act["Vz"]),
         fmt(f["As_required_including_min_mm2"]),
         fmt(f["As_provided_tension_mm2"]),fmt(s["tau_v_MPa"]),fmt(s["tau_c_MPa"]),
         fmt(s["stirrup_s_upper_bound_mm"]),
         "Section OK" if f["provided_isolated_flexure_screen_ok"] else f["status"],
         "Section OK" if s["provided_isolated_shear_screen_ok"] else s["status"]))
    allchecks=table(("Mode","U case","Beam element","End","My signed (kNm)","Vz signed (kN)",
       "Req As (mm2)","Assumed As (mm2)","tau v (MPa)","tau c (MPa)","Max stirrup s (mm)",
       "Flexure section","Shear section"),all_rows)
    return f'''<h3>6.1 Reusable beam flexure and vertical shear — actual signed OpenSees actions</h3>
<p>This report now runs the independent
<a href="https://github.com/FabinGurung/jp-structural-analysis/blob/main/r6p30/beam_design.py">IS456 beam strength module</a>
on <strong>all {count} actual OpenSees beam-end combinations</strong>. For each end and
combination, the My bending moment and Vz shear are paired from the
<strong>same six-component signed action vector</strong>. The flexible and
rigid-in-plane models are evaluated separately.</p>
{summary}
<h3>6.1.1 Reproducible equations and reinforcement</h3>
<p><b>Flexure:</b> x<sub>u</sub>=0.87f<sub>y</sub>A<sub>s</sub>/(0.36f<sub>ck</sub>b);
M<sub>u,R</sub>=0.87f<sub>y</sub>A<sub>s</sub>(d−0.42x<sub>u</sub>).
Required steel is obtained from the singly reinforced equilibrium equation,
with IS456 minimum 0.85bd/f<sub>y</sub>, maximum 0.04bD, and
Fe500 x<sub>u,max</sub>/d=0.46. No impossible reinforcement is fabricated if
the demand exceeds the singly reinforced section limit.</p>
<p><b>Shear:</b> τ<sub>v</sub>=|V<sub>z</sub>|/(bd).
The concrete τ<sub>c</sub> is interpolated from
<a href="{CODE_URL}">IS 456 Table 19</a> (M25; assumed continuously anchored
longitudinal bars). Table 20 limits maximum concrete shear stress.
Stirrups: V<sub>us</sub>=0.87f<sub>yv</sub>A<sub>sv</sub>d/s, with
f<sub>yv</sub>≤415 MPa and s not exceeding the minimum steel,
0.75d, 300mm, or required-strength limits. Assumed
two-legged Ø8 @150mm ties are checked—not assigned as an issued schedule.</p>
<div class="wire"><b>Boundary:</b> the U± combinations contain synthetic
1.2DL+1.5LL±10kN HX <em>diagnostic</em> actions, not the NBC seismic code
envelope. Signed Mz, Vy, torsion T and axial N are preserved in JSON but
have <strong>not</strong> undergone their interaction checks.
Results apply at the <em>OpenSees member ends</em>, not a source-confirmed
code critical section one effective depth away from a support face.
Seismic ductile detailing, bar development/anchorage, joint shear,
deflection/crack control and true building acceptance remain outside this
bounded isolated section calculation. Do not label these as issued designs.</div>
<p><a href="reports/example-sar/beam-end-checks.csv">
Download all {count} beam-end checks (CSV)</a> ·
<a href="reports/example-sar/example-sar-numbers.json">
Open source, six signed forces and formulas (JSON)</a></p>
<details><summary><strong>Inspect the {count} evaluated beam ends</strong></summary>
{allchecks}</details><h3>6.2 Other illustrative member examples</h3>'''
