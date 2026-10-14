"""Small UML -> draw.io XML writer used by Blueprint for this project.

Every diagram element is written as an <object> carrying traceability
properties (req = source requirement IDs, statut = E/I/U) so the .drawio files
stay editable AND traceable. Coordinates passed to v() are ABSOLUTE; they are
converted to container-relative coordinates automatically.
"""
from xml.sax.saxutils import escape
import os

def _a(s):
    return escape(str(s), {'"': "&quot;", "\n": "&#xa;"})

# ---------------------------------------------------------------- styles
FONT = "fontSize=12;"
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;whiteSpace=nowrap;" + FONT
USECASE = "ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" + FONT
BOUNDARY = ("swimlane;startSize=30;html=1;whiteSpace=wrap;container=1;collapsible=0;"
            "fillColor=none;swimlaneFillColor=#ffffff;fontStyle=1;" + FONT)
ASSOC = "endArrow=none;html=1;rounded=0;"
ASSOC_L = ASSOC + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
DEP = "endArrow=open;endSize=10;dashed=1;html=1;rounded=0;fontSize=11;labelBackgroundColor=#ffffff;"
GEN = "endArrow=block;endFill=0;endSize=14;html=1;rounded=0;"
NOTE = ("shape=note;whiteSpace=wrap;html=1;size=14;fillColor=#fff2cc;strokeColor=#d6b656;"
        "align=left;verticalAlign=top;spacingLeft=6;spacingTop=2;fontSize=11;")
WARNNOTE = NOTE.replace("#fff2cc", "#f8cecc").replace("#d6b656", "#b85450")
ANCHOR = "endArrow=none;dashed=1;html=1;strokeColor=#999999;rounded=0;"
TITLE = "text;html=1;fontSize=16;fontStyle=1;align=left;verticalAlign=top;whiteSpace=wrap;"
TEXT = "text;html=1;fontSize=11;align=left;verticalAlign=top;whiteSpace=wrap;"
INFERRED = "dashed=1;dashPattern=6 3;"

CLASS = ("swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;"
         "startSize=40;horizontalStack=0;resizeParent=1;resizeLast=0;collapsible=0;marginBottom=0;"
         "html=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;" + FONT)
ENUM = CLASS.replace("#dae8fc", "#e1d5e7").replace("#6c8ebf", "#9673a6")
EXT_CLASS = CLASS.replace("#dae8fc", "#f5f5f5").replace("#6c8ebf", "#666666")
ATTRS = ("text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;"
         "overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;html=1;whiteSpace=wrap;fontSize=11;")
LINK = "endArrow=none;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;fontSize=11;"
COMPO = "endArrow=none;startArrow=diamondThin;startFill=1;startSize=16;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;"
INHERIT = "endArrow=block;endFill=0;endSize=14;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;"
ELABEL = "edgeLabel;resizable=0;html=1;fontSize=11;labelBackgroundColor=#ffffff;"

STATE = "rounded=1;whiteSpace=wrap;html=1;arcSize=40;fillColor=#d5e8d4;strokeColor=#82b366;" + FONT
INITIAL = "ellipse;html=1;fillColor=#000000;strokeColor=#000000;"
FINAL = "ellipse;html=1;shape=endState;fillColor=#000000;strokeColor=#000000;"
TRANS = ("endArrow=open;endSize=10;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;fontSize=11;"
         "labelBackgroundColor=#ffffff;")
STRAIGHT = "endArrow=open;endSize=10;html=1;rounded=0;fontSize=11;labelBackgroundColor=#ffffff;"

ACTION = "rounded=1;whiteSpace=wrap;html=1;arcSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;"
DECISION = "rhombus;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;"
BAR = "html=1;fillColor=#000000;strokeColor=none;"
TIMEEV = "shape=collate;whiteSpace=nowrap;html=1;fillColor=#ffffff;labelPosition=right;verticalLabelPosition=middle;align=left;verticalAlign=middle;spacingLeft=4;fontSize=11;"
LANE = "swimlane;startSize=30;html=1;whiteSpace=wrap;collapsible=0;fillColor=#f5f5f5;swimlaneFillColor=#ffffff;fontStyle=1;" + FONT
FLOW = ("endArrow=open;endSize=10;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;fontSize=11;"
        "labelBackgroundColor=#ffffff;")

LIFELINE = ("shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;"
            "collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;size=50;" + FONT)
LIFEACTOR = LIFELINE + "participant=umlActor;verticalAlign=bottom;spacingBottom=-16;labelBackgroundColor=#ffffff;"
SYNC = "html=1;verticalAlign=bottom;endArrow=block;endFill=1;rounded=0;fontSize=11;"
ASYNC = "html=1;verticalAlign=bottom;endArrow=open;endSize=10;rounded=0;fontSize=11;"
RET = "html=1;verticalAlign=bottom;endArrow=open;endSize=10;dashed=1;rounded=0;fontSize=11;strokeColor=#666666;fontColor=#444444;"
FRAME = ("shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;width=70;height=24;fillColor=none;"
         "fontStyle=1;fontSize=11;align=left;spacingLeft=4;")
SEP = "endArrow=none;dashed=1;html=1;rounded=0;strokeColor=#000000;"
GUARD = "text;html=1;fontSize=11;align=left;verticalAlign=middle;fontStyle=2;"


class Diagram:
    def __init__(self, page_id, name):
        self.page_id, self.name = page_id, name
        self.cells, self.origin, self.ids = [], {"1": (0, 0)}, set()
        self.maxx, self.maxy = 800, 600

    def _id(self, cid):
        assert cid not in self.ids and cid not in ("0", "1"), cid
        self.ids.add(cid)
        return cid

    @staticmethod
    def _props(req=None, statut=None, extra=None):
        p = ""
        if req:
            p += f' req="{_a(req)}"'
        if statut:
            p += f' statut="{_a(statut)}"'
        for k, val in (extra or {}).items():
            p += f' {k}="{_a(val)}"'
        return p

    def v(self, cid, label, x, y, w, h, style, parent="1", req=None, statut=None, extra=None):
        self._id(cid)
        ox, oy = self.origin[parent]
        self.origin[cid] = (x, y)
        self.maxx, self.maxy = max(self.maxx, x + w), max(self.maxy, y + h)
        self.cells.append(
            f'<object id="{_a(cid)}" label="{_a(label)}"{self._props(req, statut, extra)}>'
            f'<mxCell style="{_a(style)}" vertex="1" parent="{_a(parent)}">'
            f'<mxGeometry x="{x - ox}" y="{y - oy}" width="{w}" height="{h}" as="geometry"/>'
            f'</mxCell></object>')
        return cid

    def e(self, cid, src, tgt, label="", style=ASSOC, points=None, req=None, statut=None,
          sp=None, tp=None, src_lbl=None, tgt_lbl=None, mid_lbl=None, extra=None,
          src_off=(0, -10), tgt_off=(0, -10)):
        self._id(cid)
        s = f' source="{_a(src)}"' if src else ""
        t = f' target="{_a(tgt)}"' if tgt else ""
        geo = '<mxGeometry relative="1" as="geometry">'
        if sp:
            geo += f'<mxPoint x="{sp[0]}" y="{sp[1]}" as="sourcePoint"/>'
        if tp:
            geo += f'<mxPoint x="{tp[0]}" y="{tp[1]}" as="targetPoint"/>'
        if points:
            geo += '<Array as="points">' + "".join(
                f'<mxPoint x="{px}" y="{py}"/>' for px, py in points) + "</Array>"
        geo += "</mxGeometry>"
        self.cells.append(
            f'<object id="{_a(cid)}" label="{_a(label)}"{self._props(req, statut, extra)}>'
            f'<mxCell style="{_a(style)}" edge="1" parent="1"{s}{t}>{geo}</mxCell></object>')
        for suffix, txt, pos, off in (("s", src_lbl, -1, src_off), ("t", tgt_lbl, 1, tgt_off),
                                      ("m", mid_lbl, 0, (0, -10))):
            if txt:
                lid = self._id(f"{cid}_{suffix}")
                self.cells.append(
                    f'<mxCell id="{lid}" value="{_a(txt)}" style="{_a(ELABEL)}" vertex="1" '
                    f'connectable="0" parent="{_a(cid)}"><mxGeometry x="{pos}" relative="1" '
                    f'as="geometry"><mxPoint x="{off[0]}" y="{off[1]}" as="offset"/></mxGeometry></mxCell>')
        return cid

    # ---- composite helpers
    def note(self, cid, text, x, y, w, h, warn=False, req=None, attach=None):
        self.v(cid, text, x, y, w, h, WARNNOTE if warn else NOTE, req=req,
               statut="WARN" if warn else None)
        for i, a in enumerate(attach or []):
            self.e(f"{cid}_a{i}", cid, a, style=ANCHOR)
        return cid

    def cls(self, cid, name, attrs, x, y, w, req=None, statut="E", style=CLASS, stereo=None):
        head = (f"«{stereo}»<br>" if stereo else "") + f"<b>{name}</b>"
        if statut and statut != "E":
            head += f" <i>[{statut}]</i>"
            style = style + INFERRED if statut == "I" else style
        h_attr = max(1, len(attrs)) * 16 + 10
        self.v(cid, head, x, y, w, 40 + h_attr, style.replace("fontStyle=1;", "fontStyle=0;"),
               req=req, statut=statut)
        self.v(cid + "_attrs", "<br>".join(attrs) if attrs else "&nbsp;", x, y + 40, w, h_attr,
               ATTRS, parent=cid)
        return cid

    def title(self, text, sub=None, x=20, y=10, w=1100):
        self.v("title", f"<b>{text}</b>" + (f"<br><font style='font-size:11px'>{sub}</font>" if sub else ""),
               x, y, w, 50 if sub else 30, TITLE)

    def legend(self, x, y, lines, w=330):
        h = 20 + 15 * len(lines)
        self.v("legend", "<b>Légende</b><br>" + "<br>".join(lines), x, y, w, h,
               "rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacingLeft=6;"
               "fontSize=10;fillColor=#f5f5f5;strokeColor=#999999;")

    def xml(self):
        pw, ph = int(self.maxx + 60), int(self.maxy + 60)
        return ('<mxfile host="Blueprint" type="device">\n'
                f'  <diagram id="{_a(self.page_id)}" name="{_a(self.name)}">\n'
                f'    <mxGraphModel dx="{pw}" dy="{ph}" grid="1" gridSize="10" guides="1" tooltips="1" '
                f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{pw}" '
                f'pageHeight="{ph}" math="0" shadow="0">\n      <root>\n'
                '        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n        '
                + "\n        ".join(self.cells)
                + "\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n")

    def write(self, path, allow_overwrite=None):
        # Regeneration of files produced by THIS build is opted into via BP_REGEN=1;
        # pre-existing diagrams are never overwritten silently.
        if allow_overwrite is None:
            allow_overwrite = os.environ.get("BP_REGEN") == "1"
        if os.path.exists(path) and not allow_overwrite:
            raise FileExistsError(f"refusing to overwrite {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.xml())
        return path


# ---------------------------------------------------------------- sequence helper
class Seq:
    """Sequence diagram with alt/opt frames.  Steps:
    ("msg", src, dst, label, kind)  kind in sync|async|ret
    ("self", who, label)
    ("note", over, text)            note right of a lifeline
    ("frame", op, guard, [participants span or None])  opens a frame
    ("else", guard)                 separator in current frame
    ("end",)                        closes frame
    ("gap", px)
    """
    def __init__(self, d, parts, x0=40, y0=90, spacing=210, top_gap=40):
        self.d, self.parts = d, parts
        self.cx = {p[0]: x0 + 60 + i * spacing for i, p in enumerate(parts)}
        self.x0, self.y0, self.spacing, self.top_gap = x0, y0, spacing, top_gap

    def build(self, steps, req_by_step=None):
        d, y = self.d, self.y0 + 50 + self.top_gap
        rows, stack, frames, n = [], [], [], 0
        depth = 0
        for st in steps:
            k = st[0]
            if k == "msg":
                y += 15 * st[3].count("<br>")
                rows.append((st, y)); y += 44
            elif k == "self":
                rows.append((st, y)); y += 58 + 15 * st[2].count("<br>")
            elif k == "note":
                rows.append((st, y)); y += st[3] if len(st) > 3 else 52
            elif k == "frame":
                stack.append({"op": st[1], "guards": [(st[2], y)], "y0": y, "span": st[3] if len(st) > 3 else None,
                              "depth": len(stack)})
                y += 48
            elif k == "else":
                stack[-1]["guards"].append((st[1], y)); y += 48
            elif k == "end":
                f = stack.pop(); f["y1"] = y + 6; frames.append(f); y += 34
            elif k == "gap":
                y += st[1]
        height = y + 30 - self.y0
        for pid, label, kind in self.parts:
            st = LIFEACTOR if kind == "actor" else LIFELINE
            if kind == "ext":
                st += "fillColor=#f5f5f5;strokeColor=#666666;"
            d.v(pid, label, self.cx[pid] - 60, self.y0, 120, height, st)
        xmin = min(self.cx.values()) - 85
        xmax = max(self.cx.values()) + 85
        for i, f in enumerate(frames):
            if f["span"]:
                fx0 = min(self.cx[p] for p in f["span"]) - 80 + 8 * f["depth"]
                fx1 = max(self.cx[p] for p in f["span"]) + 80 - 8 * f["depth"]
            else:
                fx0, fx1 = xmin + 8 * f["depth"], xmax - 8 * f["depth"]
            fid = d.v(f"frame{i}", f["op"], fx0, f["y0"], fx1 - fx0, f["y1"] - f["y0"],
                      FRAME + ("width=60;" if len(f["op"]) < 6 else "width=110;"))
            for j, (g, gy) in enumerate(f["guards"]):
                if j > 0:
                    d.e(f"frame{i}_sep{j}", None, None, style=SEP, sp=(fx0, gy), tp=(fx1, gy))
                d.v(f"frame{i}_g{j}", f"[{g}]", fx0 + (115 if (j == 0 and len(f['op']) >= 6) else (65 if j == 0 else 8)),
                    gy + 2, min(560, fx1 - fx0 - 120), 22, GUARD, parent=fid)
        bottom = y + 30
        for idx, (st, y) in enumerate(rows):
            k, mid = st[0], f"m{idx + 1:02d}"
            if k == "msg":
                _, s, t, label, kind = st[:5]
                style = {"sync": SYNC, "async": ASYNC, "ret": RET}[kind]
                fy = round((y - self.y0) / height, 4)
                d.e(mid, s, t, label, style + f"exitX=0.5;exitY={fy};entryX=0.5;entryY={fy};"
                    "exitDx=0;exitDy=0;entryDx=0;entryDy=0;", req=st[5] if len(st) > 5 else None)
            elif k == "self":
                _, s, label = st[:3]
                x = self.cx[s]
                fy1 = round((y - self.y0) / height, 4); fy2 = round((y + 28 - self.y0) / height, 4)
                d.e(mid, s, s, label, SYNC + f"exitX=0.5;exitY={fy1};entryX=0.5;entryY={fy2};align=left;"
                    "spacingLeft=6;verticalAlign=middle;", points=[(x + 40, y), (x + 40, y + 28)],
                    req=st[3] if len(st) > 3 else None)
            elif k == "note":
                _, over, text = st[:3]
                h = (st[3] if len(st) > 3 else 52) - 8
                w = st[4] if len(st) > 4 else 300
                d.v(f"n{idx + 1:02d}", text, self.cx[over] + 14, y - 14, w, h, NOTE)
        return bottom
