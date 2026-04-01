from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "/Users/abhijit/Documents/Claude/figma-chronicle-debug.pdf"

# ── Styles ─────────────────────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle("DocTitle",
        fontName="Helvetica-Bold", fontSize=20, leading=26,
        textColor=colors.HexColor("#1a1a1a"), spaceAfter=4)

    subtitle = ParagraphStyle("DocSubtitle",
        fontName="Helvetica", fontSize=11, leading=15,
        textColor=colors.HexColor("#71717a"), spaceAfter=18)

    h1 = ParagraphStyle("H1",
        fontName="Helvetica-Bold", fontSize=13, leading=18,
        textColor=colors.HexColor("#5B4BF5"), spaceBefore=18, spaceAfter=6,
        borderPadding=(0, 0, 3, 0))

    h2 = ParagraphStyle("H2",
        fontName="Helvetica-Bold", fontSize=11, leading=15,
        textColor=colors.HexColor("#1a1a1a"), spaceBefore=12, spaceAfter=4)

    body = ParagraphStyle("Body",
        fontName="Helvetica", fontSize=9, leading=14,
        textColor=colors.HexColor("#1a1a1a"), spaceAfter=6)

    code = ParagraphStyle("Code",
        fontName="Courier", fontSize=7.5, leading=11,
        textColor=colors.HexColor("#1a1a1a"),
        backColor=colors.HexColor("#f4f4f5"),
        borderPadding=(6, 8, 6, 8), spaceAfter=8)

    label_ok = ParagraphStyle("LabelOk",
        fontName="Helvetica", fontSize=9, leading=13,
        textColor=colors.HexColor("#16a34a"))

    label_fail = ParagraphStyle("LabelFail",
        fontName="Helvetica", fontSize=9, leading=13,
        textColor=colors.HexColor("#dc2626"))

    note = ParagraphStyle("Note",
        fontName="Helvetica-Oblique", fontSize=8.5, leading=13,
        textColor=colors.HexColor("#52525b"),
        backColor=colors.HexColor("#fef9c3"),
        borderPadding=(6, 8, 6, 8), spaceAfter=8)

    return dict(title=title, subtitle=subtitle, h1=h1, h2=h2,
                body=body, code=code, label_ok=label_ok,
                label_fail=label_fail, note=note)

S = make_styles()

# ── Helpers ─────────────────────────────────────────────────────────────────

def H(tag, text): return Paragraph(text, S[tag])
def gap(n=6):     return Spacer(1, n)
def rule():       return HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#e4e4e7"),
                                    spaceAfter=6, spaceBefore=2)

BOX_BG   = colors.HexColor("#f4f4f5")
BOX_FAIL = colors.HexColor("#fff1f2")
BOX_OK   = colors.HexColor("#f0fdf4")
BOX_WARN = colors.HexColor("#fffbeb")
BOX_BLUE = colors.HexColor("#f5f3ff")
PURPLE   = colors.HexColor("#5B4BF5")

def code_block(text, bg=BOX_BG):
    """Monospace block with coloured background."""
    lines = text.strip("\n").split("\n")
    para_lines = "<br/>".join(
        ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;")
        for ln in lines
    )
    style = ParagraphStyle("CB", parent=S["code"], backColor=bg,
                           borderPadding=(7, 9, 7, 9))
    return Paragraph(para_lines, style)

def status_row(symbol, text, ok=True):
    color = "#16a34a" if ok else "#dc2626"
    return Paragraph(f'<font color="{color}"><b>{symbol}</b></font>  {text}', S["body"])

def section_box(title, items, bg=BOX_BG, title_color="#1a1a1a"):
    """Titled coloured box."""
    header_style = ParagraphStyle("BH", fontName="Helvetica-Bold",
                                  fontSize=9, textColor=colors.HexColor(title_color))
    body_style   = ParagraphStyle("BB", fontName="Courier", fontSize=7.5,
                                  leading=11, textColor=colors.HexColor("#1a1a1a"))
    rows = [[Paragraph(title, header_style)]]
    for item in items:
        rows.append([Paragraph(item.replace(" ", "&nbsp;").replace("<","&lt;").replace(">","&gt;"), body_style)])
    t = Table(rows, colWidths=["100%"])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [6, 6, 6, 6]),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [bg]),
    ]))
    return t

# ── Content ──────────────────────────────────────────────────────────────────

def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title="Figma → Chronicle Plugin: Debug Reference",
        author="Chronicle HQ"
    )

    W = A4[0] - 36*mm   # usable width

    story = []

    # ── Cover ────────────────────────────────────────────────────────────────
    story += [
        gap(8),
        H("title", "Figma → Chronicle Plugin"),
        H("subtitle", "Debug Reference  ·  Clipboard Integration Issue  ·  2026-03-31"),
        rule(),
        gap(4),
    ]

    # ── 1. Architecture ──────────────────────────────────────────────────────
    story += [H("h1", "1.  Architecture Overview")]

    arch = """\
┌──────────────────────────────────────────────────────────────────┐
│                    FIGMA DESKTOP  (Electron)                     │
│                                                                  │
│  ┌────────────────────────┐      ┌────────────────────────────┐  │
│  │  PLUGIN MAIN THREAD    │      │    PLUGIN UI IFRAME        │  │
│  │  dist/code.js          │      │    src/ui.html             │  │
│  │                        │      │                            │  │
│  │  • QuickJS VM          │      │  • Sandboxed Chromium      │  │
│  │  • Figma API access    │ msg  │  • sandbox="allow-scripts" │  │
│  │  • NO browser APIs     │◄────►│  • NULL origin             │  │
│  │    (no btoa, fetch…)   │      │  • Has DOM, Canvas         │  │
│  │  • Exports node data   │      │  • Handles clipboard       │  │
│  └────────────────────────┘      └────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘"""
    story += [code_block(arch), gap(4)]

    story += [
        H("body", "<b>Two separate JS environments</b> that can only communicate via "
          "<b>postMessage()</b>. The main thread has full Figma API access but no browser "
          "APIs. The UI iframe has browser APIs (DOM, canvas, clipboard) but runs in a "
          "heavily sandboxed context with a <b>null origin</b>."),
        gap(4),
    ]

    # ── 2. Data Flow ─────────────────────────────────────────────────────────
    story += [H("h1", "2.  Data Flow: User Clicks \"Copy to Clipboard\"")]

    flow = """\
USER CLICKS BUTTON
      │
      ▼
[ui.html]  requestExport()
  postMessage → { type:'EXPORT', format:'PNG'|'SVG', scale:1|2|3 }
      │
      ▼
[code.js]  figma.ui.onmessage()
  node = figma.currentPage.selection[0]
      │
      ├── SVG  →  node.exportAsync({ format:'SVG_STRING' })
      │                 returns: string
      │
      └── PNG  →  node.exportAsync({ format:'PNG', constraint:{SCALE,n} })
                        returns: Uint8Array
                              │
                        uint8ToBase64()   ← pure JS (no btoa — not in QuickJS)
                              │
      ◄────────── postMessage { type:'EXPORT_RESULT', format, data:string }
      │
      ▼
[ui.html]  sendToChronicle(data, format)
  SVG  →  svgToDataUrl()  →  parse dims  →  canvas  →  PNG data URL
  PNG  →  'data:image/png;base64,' + data
      │
      ▼
  writeToClipboard(dataUrl)   ◄── FAILURE POINT (see Section 3)"""
    story += [code_block(flow), gap(4)]

    # ── 3. Clipboard Attempts ─────────────────────────────────────────────────
    story += [H("h1", "3.  Clipboard Attempts & Why Each Fails")]

    # Method 1
    story += [H("h2", "Method 1 — ClipboardItem API  (navigator.clipboard.write)")]
    m1_code = """\
const blob = new Blob([bytes], { type: 'image/png' });
await navigator.clipboard.write([
  new ClipboardItem({ 'image/png': blob })
]);"""
    story += [
        code_block(m1_code, BOX_FAIL),
        status_row("✗  FAILS", "Figma's null-origin iframe cannot obtain the <b>clipboard-write</b> "
                   "Permission API grant that ClipboardItem requires. Throws → falls through.", ok=False),
        gap(8),
    ]

    # Method 2
    story += [H("h2", "Method 2 — execCommand + text/html  (tried earlier)")]
    m2_code = """\
document.addEventListener('copy', e => {
  e.clipboardData.setData('text/html', '<img src="data:image/png;base64,...">');
  e.clipboardData.setData('text/plain', '');
  e.preventDefault();
});
document.execCommand('copy');"""
    story += [
        code_block(m2_code, BOX_FAIL),
        status_row("✗  FAILS", "<b>execCommand works</b> (text WAS written to clipboard) but both "
                   "Figma and Chronicle <b>sanitize data: URLs</b> from HTML paste for security → "
                   "blank &lt;img&gt; → blank text box on paste.", ok=False),
        gap(8),
    ]

    # Method 3
    story += [H("h2", "Method 3 — contenteditable + select + execCommand  (current)")]
    m3_code = """\
const img  = new Image();
img.src    = dataUrl;           // data:image/png;base64,...
const host = document.createElement('div');
host.setAttribute('contenteditable', 'true');
host.appendChild(img);
document.body.appendChild(host);
const range = document.createRange();
range.selectNodeContents(host);
window.getSelection().addRange(range);
document.execCommand('copy');   // browser should write image/png natively"""
    story += [
        code_block(m3_code, BOX_FAIL),
        status_row("✗  STILL FAILS", "In theory, Chromium should encode the selected &lt;img&gt; as "
                   "native <b>image/png</b> bytes. In practice, Figma's sandbox appears to prevent "
                   "this — only text/html (with stripped data: URL) reaches the clipboard.", ok=False),
        gap(8),
    ]

    # ── 4. Root Cause ─────────────────────────────────────────────────────────
    story += [H("h1", "4.  Root Cause")]

    rc = """\
Figma plugin UI iframe:   sandbox="allow-scripts"  (no allow-same-origin)
                          → Origin is NULL

  navigator.clipboard.writeText()   ✓  works  (plain text, no permission needed)
  navigator.clipboard.write()       ✗  blocked (clipboard-write perm, null origin denied)
  document.execCommand('copy')      ✓  works  (text/html written to clipboard)
  …but clipboard holds text/html,   ✗  Figma & Chronicle both strip data: URLs
    not image/png bytes                 → blank on paste"""
    story += [code_block(rc, BOX_WARN), gap(4)]

    story += [
        H("body", "The blocker is that <b>no method available to a null-origin sandboxed iframe "
          "can write raw image/png bytes to the OS clipboard</b> without the clipboard-write "
          "permission, which Figma's sandbox does not grant."),
        gap(4),
    ]

    # ── 5. What Engineer Should Investigate ──────────────────────────────────
    story += [H("h1", "5.  Recommended Investigation Paths")]

    options = [
        ("A — Figma Plugin API",
         "Does Figma expose any undocumented plugin API to write image bytes directly to the "
         "native OS clipboard?\n"
         "e.g.  figma.clipboard.setImage(bytes: Uint8Array)\n"
         "→ Check Figma Plugin API changelog / community forums / Figma Staff replies",
         BOX_BG),

        ("B — iframe ↔ Figma postMessage bridge",
         "Can the plugin postMessage to a parent Figma frame that has a real origin,\n"
         "which then calls navigator.clipboard.write() on behalf of the plugin?\n"
         "→ Check if Figma blocks cross-frame clipboard delegation",
         BOX_BG),

        ("C — Electron-specific clipboard API",
         "Figma Desktop is Electron. Does Figma expose electron.clipboard\n"
         "or nativeImage to plugins via a custom preload script?\n"
         "→ Check Figma's internal / undocumented plugin capabilities",
         BOX_BG),

        ("D — Chronicle API  (RECOMMENDED — skip clipboard entirely)",
         "The sendToChronicle() function in ui.html is already abstracted.\n"
         "When Chronicle's API is available, replace writeToClipboard()\n"
         "with a single fetch() POST of the PNG bytes.\n"
         "→ Abhijit works at Chronicle and can request early API access.",
         BOX_BLUE),
    ]

    for title, desc, bg in options:
        title_style = ParagraphStyle("OptT", fontName="Helvetica-Bold",
                                     fontSize=9, textColor=PURPLE if bg == BOX_BLUE else colors.HexColor("#1a1a1a"))
        desc_style  = ParagraphStyle("OptD", fontName="Helvetica", fontSize=8.5,
                                     leading=13, textColor=colors.HexColor("#1a1a1a"))
        desc_safe   = desc.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br/>")
        t = Table([
            [Paragraph(title, title_style)],
            [Paragraph(desc_safe, desc_style)],
        ], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), bg),
            ("TOPPADDING",   (0,0), (-1,-1), 8),
            ("BOTTOMPADDING",(0,0), (-1,-1), 8),
            ("LEFTPADDING",  (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("LINEBELOW",    (0,0), (-1,0),  0.5, colors.HexColor("#e4e4e7")),
        ]))
        story += [t, gap(6)]

    # ── 6. Key Files ─────────────────────────────────────────────────────────
    story += [H("h1", "6.  Key Files")]

    table_data = [
        ["File", "Role", "Critical Function"],
        ["manifest.json",  "Plugin config — entry points, sandbox permissions", "networkAccess.allowedDomains"],
        ["dist/code.js",   "Main thread — Figma API, export, base64 encode",    "uint8ToBase64()  (pure JS, no btoa)"],
        ["src/ui.html",    "UI iframe — canvas render, clipboard attempts",      "writeToClipboard()  (~line 305)"],
    ]

    hdr = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5,
                          textColor=colors.white)
    cel = ParagraphStyle("TC", fontName="Helvetica", fontSize=8.5, leading=12,
                          textColor=colors.HexColor("#1a1a1a"))
    cod = ParagraphStyle("TCo", fontName="Courier", fontSize=7.5, leading=11,
                          textColor=colors.HexColor("#1a1a1a"))

    tbl_rows = [
        [Paragraph(c, hdr) for c in table_data[0]],
    ]
    for row in table_data[1:]:
        tbl_rows.append([
            Paragraph(row[0], cod),
            Paragraph(row[1], cel),
            Paragraph(row[2], cod),
        ])

    col_w = [W * f for f in [0.24, 0.40, 0.36]]
    tbl = Table(tbl_rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  PURPLE),
        ("BACKGROUND",   (0,1), (-1,-1), colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#f9f9fb")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#e4e4e7")),
        ("TOPPADDING",   (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0), (-1,-1), 7),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story += [tbl, gap(16)]

    # ── Footer note ───────────────────────────────────────────────────────────
    story += [
        rule(),
        Paragraph(
            "The <b>entire blocker</b> lives in <font face='Courier'>writeToClipboard()</font> "
            "inside <font face='Courier'>src/ui.html</font>. All other parts of the plugin "
            "(Figma export, base64 encoding, canvas rendering, UI) work correctly.",
            ParagraphStyle("Footer", fontName="Helvetica", fontSize=8.5, leading=13,
                           textColor=colors.HexColor("#52525b"),
                           backColor=colors.HexColor("#f5f3ff"),
                           borderPadding=(8, 10, 8, 10))
        ),
    ]

    doc.build(story)
    print(f"PDF saved → {OUTPUT}")

build()
