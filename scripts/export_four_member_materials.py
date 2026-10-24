"""Export the current EpiScope report, policy brief, and slides.

Uses the installed Chrome browser for PDF rendering and Python's standard
library for a portable PowerPoint Open XML export.
"""
from __future__ import annotations

import html
import re
import subprocess
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
MEMBERS = [
    ("Md. Samin Osman", "0222220005101042"),
    ("Robiul Hassan", "0222220005101043"),
    ("Walid Talal", "0222220005101045"),
    ("Md. Mahafujul Alam", "0222220005101066"),
]


def update_slides() -> str:
    path = DOCS / "presentation.html"
    source = path.read_text(encoding="utf-8")
    source = source.replace("grid-template-columns:repeat(3,1fr);gap:.75rem;margin-top:1.5rem", "grid-template-columns:repeat(4,1fr);gap:.75rem;margin-top:1.5rem")
    source = source.replace("Robiul Hassan</strong><small>0222220005101043</small>", "Robiul Hassan</strong><small>0222220005101043</small>")
    opening = re.search(r'<div class="people">.*?</div></div><div class="foot">', source)
    if opening:
        people = '<div class="people">' + ''.join(
            f'<div class="person"><strong>{html.escape(name)}</strong><small>{idno}</small><p>{role}</p></div>'
            for (name, idno), role in zip(MEMBERS, ["Evaluation and planning", "Pipeline and incremental data", "Privacy and limitations", "Dashboard and serving"])
        ) + '</div></div><div class="foot">'
        source = source[:opening.start()] + people + source[opening.end():]
    sections = list(re.finditer(r'<section class="slide[^>]*>.*?</section>', source, re.S))
    speakers = ["Robiul Hassan"] * 4 + ["Md. Samin Osman"] * 2 + ["Md. Mahafujul Alam"] + ["Walid Talal"] * 2
    labels = ["Robiul · opening", "Robiul Hassan", "Robiul Hassan", "Robiul · Colab demo", "Md. Samin Osman", "Md. Samin Osman", "Md. Mahafujul Alam", "Walid Talal", "Walid Talal · close"]
    for idx in reversed(range(min(len(sections), 9))):
        match = sections[idx]
        block = match.group(0)
        block = re.sub(r'data-speaker="[^"]*"', f'data-speaker="{speakers[idx]}"', block, count=1)
        block = re.sub(r'<span class="speaker">.*?</span>', f'<span class="speaker">{labels[idx]}</span>', block, count=1)
        if idx == 0:
            block = block.replace("with Md Samin Osman and Md Mahafujul Alam", "with Md. Samin Osman, Walid Talal, and Md. Mahafujul Alam")
        if idx == 7:
            block = block.replace("Md Mahafujul Alam", "Walid Talal")
        if idx == 8:
            start = block.find('<div class="people">')
            end_marker = '</div></div><p class="lead"'
            end = block.find(end_marker, start)
            if start >= 0 and end >= 0:
                cards = '<div class="people">'
                cards += '<div class="person"><strong>Robiul · slides 1–4</strong><small>~4 min, including demo cue</small><p>Architecture, data quality, incremental input</p></div>'
                cards += '<div class="person"><strong>Samin · slides 5–6</strong><small>~4 min</small><p>Detection, forecasts, planning</p></div>'
                cards += '<div class="person"><strong>Mahafujul · slide 7</strong><small>~3 min</small><p>Dashboard and serving</p></div>'
                cards += '<div class="person"><strong>Walid · slides 8–9</strong><small>~3 min</small><p>Privacy, limitations, recommendations, close</p></div></div>'
                block = block[:start] + cards + block[end + len('</div></div>'):]
            block = block.replace("Md Mahafujul Alam · close", "Walid Talal · close")
        source = source[:match.start()] + block + source[match.end():]
    path.write_text(source, encoding="utf-8")
    return source


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
    def handle_data(self, data: str):
        value = re.sub(r"\s+", " ", data).strip()
        if value:
            self.parts.append(value)


def slide_deck(source: str, target: Path) -> None:
    sections = re.findall(r'<section class="slide[^>]*>.*?</section>', source, re.S)
    slides = []
    for index, section in enumerate(sections):
        title = re.search(r'<h[12][^>]*>(.*?)</h[12]>', section, re.S)
        parser = TextExtractor(); parser.feed(section)
        title_text = re.sub(r"<[^>]+>", " ", title.group(1) if title else "EpiScope")
        title_text = html.unescape(re.sub(r"\s+", " ", title_text)).strip()
        flat = [x for x in parser.parts if x not in title_text and not re.fullmatch(r"\d{2} / \d{2}", x)]
        speaker = re.search(r'data-speaker="([^"]+)"', section)
        body = []
        for item in flat:
            if item.startswith(("EPISCOPE", "0", "01 /", "02 /", "03 /", "04 /", "05 /", "06 /", "07 /", "08 /")):
                continue
            if len(item) > 180: item = item[:177].rsplit(" ", 1)[0] + "…"
            if item and item != title_text and item not in body: body.append(item)
        slides.append((title_text, speaker.group(1) if speaker else "EpiScope team", body[:7]))

    def run(text, x, y, size, color, bold=False):
        return f'<a:r><a:rPr lang="en-US" sz="{size}" b="{1 if bold else 0}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Aptos"/></a:rPr><a:t>{escape(text)}</a:t></a:r>'
    slide_xmls = []
    for title, speaker, body in slides:
        paragraphs = [f'<a:p><a:pPr/><a:r><a:rPr lang="en-US" sz="3000" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:latin typeface="Aptos Display"/></a:rPr><a:t>{escape(title)}</a:t></a:r><a:endParaRPr lang="en-US"/></a:p>']
        for item in body:
            paragraphs.append(f'<a:p><a:pPr marL="300000" indent="-180000"><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="en-US" sz="1700"><a:solidFill><a:srgbClr val="D7E7EF"/></a:solidFill><a:latin typeface="Aptos"/></a:rPr><a:t>{escape(item)}</a:t></a:r><a:endParaRPr lang="en-US"/></a:p>')
        paragraphs.append(f'<a:p><a:pPr/><a:r><a:rPr lang="en-US" sz="1400" b="1"><a:solidFill><a:srgbClr val="59DDC4"/></a:solidFill><a:latin typeface="Aptos"/></a:rPr><a:t>Speaker: {escape(speaker)}</a:t></a:r><a:endParaRPr lang="en-US"/></a:p>')
        shape = '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Content"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="720000" y="700000"/><a:ext cx="10700000" cy="5100000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>' + ''.join(paragraphs) + '</p:txBody></p:sp>'
        bg = '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="092338"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
        slide_xmls.append(f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld>{bg}<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>{shape}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, value): z.writestr(name, value.encode("utf-8"))
        types = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>','<Default Extension="xml" ContentType="application/xml"/>','<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>','<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>','<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>','<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>']
        types += [f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1,len(slide_xmls)+1)]
        put('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'+''.join(types)+'</Types>')
        put('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
        sids=''.join(f'<p:sldId id="{255+i}" r:id="rId{i+2}"/>' for i in range(len(slide_xmls)))
        put('ppt/presentation.xml',f'<?xml version="1.0" encoding="UTF-8"?><p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>{sids}</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>')
        rels='<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>' + ''.join(f'<Relationship Id="rId{i+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>' for i in range(len(slide_xmls)))
        put('ppt/_rels/presentation.xml.rels',f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        master = '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
        layout = '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
        theme = '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="EpiScope"><a:themeElements><a:clrScheme name="EpiScope"><a:dk1><a:srgbClr val="092338"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="122F42"/></a:dk2><a:lt2><a:srgbClr val="F2F6F5"/></a:lt2><a:accent1><a:srgbClr val="12AD98"/></a:accent1><a:accent2><a:srgbClr val="D96568"/></a:accent2><a:accent3><a:srgbClr val="E9A13A"/></a:accent3><a:accent4><a:srgbClr val="31576B"/></a:accent4><a:accent5><a:srgbClr val="607887"/></a:accent5><a:accent6><a:srgbClr val="59DDC4"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme><a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme><a:fmtScheme name="EpiScope"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
        put('ppt/slideMasters/slideMaster1.xml',master)
        put('ppt/slideMasters/_rels/slideMaster1.xml.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>')
        put('ppt/slideLayouts/slideLayout1.xml',layout)
        put('ppt/slideLayouts/_rels/slideLayout1.xml.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>')
        put('ppt/theme/theme1.xml',theme)
        for i, xml in enumerate(slide_xmls,1):
            put(f'ppt/slides/slide{i}.xml',xml)
            put(f'ppt/slides/_rels/slide{i}.xml.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>')


def latex_to_html(source: str) -> str:
    source = re.sub(r"(?s).*?\\begin\{document\}", "", source, count=1)
    source = re.sub(r"^\\clearpage\s*", "", source)
    source = source.replace(r"\maketitle", "")
    source = source.replace(r"\clearpage", '<div class="pagebreak"></div>')
    source = source.replace(r"\onecolumn", "")
    source = re.sub(r"\\input\{[^}]+\}", "", source)
    source = source.replace(r"\begin{abstract}", '<div class="abstract"><b>Abstract.</b> ').replace(r"\end{abstract}", '</div>')
    source = source.replace(r"\begin{IEEEkeywords}", '<p><b>Index Terms—</b> ').replace(r"\end{IEEEkeywords}", '</p>')
    source = re.sub(r"\\section\*?\{([^}]+)\}", r'<h2>\1</h2>', source)
    source = re.sub(r"\\subsection\*?\{([^}]+)\}", r'<h3>\1</h3>', source)
    source = re.sub(r"\\subsubsection\*?\{([^}]+)\}", r'<h4>\1</h4>', source)
    source = re.sub(r"\\begin\{(itemize|enumerate)\}", "<ul>", source)
    source = re.sub(r"\\end\{(itemize|enumerate)\}", "</ul>", source)
    source = re.sub(r"\\item(?:\[([^]]+)\])?", lambda m: '<li>'+((m.group(1)+" ") if m.group(1) else ""), source)
    def table_rows(match):
        raw = re.sub(r"\\(?:toprule|midrule|bottomrule|hline)", "", match.group(1))
        rows = []
        for row in re.split(r"\\\\", raw):
            cells = [c.strip() for c in row.split("&")]
            cells = [re.sub(r"\\(?:textbf|emph|textit)\{([^{}]*)\}", r"\1", c) for c in cells]
            cells = [re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", c) for c in cells]
            if any(c.strip() for c in cells):
                rows.append("<tr>" + "".join("<td>" + c + "</td>" for c in cells) + "</tr>")
        return "<table>" + "".join(rows) + "</table>"
    source = re.sub(r"\\begin\{tabular\}(?:\[[^]]*\])?\{[^}]*\}(.*?)\\end\{tabular\}", table_rows, source, flags=re.S)
    source = re.sub(r"\\begin\{table\*?\}(?:\[[^]]*\])?|\\end\{table\*?\}", "", source)
    source = re.sub(r"\\caption\{([^}]+)\}", r"<caption>\1</caption>", source)
    source = re.sub(r"\\label\{[^}]+\}", "", source)
    source = re.sub(r"\\begin\{(figure|figure\*)\}.*?\\end\{\1\}", "", source, flags=re.S)
    source = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", "<h2>References</h2><p>Apache Spark documentation; Apache Parquet documentation; Bostock, Ogievetsky, and Heer, D³: Data-Driven Documents, IEEE TVCG, 2011; IEEE Reference Guide.</p>", source, flags=re.S)
    source = re.sub(r"\\bibitem\{[^}]+\}", "", source)
    source = re.sub(r"\\url\{([^}]+)\}", r"<code>\1</code>", source)
    source = re.sub(r"\\(?:textbf|emph|textit)\{([^}]+)\}", r"<b>\1</b>", source)
    source = re.sub(r"\\(?:subsection|section|title|author|IEEEauthorblockN|IEEEauthorblockA|thanks|appendices|appendix|maketitle|noindent|vfill|centering|hline|toprule|midrule|bottomrule|hspace|vspace|label|ref|cite|texttt|mathrm|left|right|quad|times|%|&)", "", source)
    source = source.replace(r"\\", " ").replace(r"\&", "&").replace(r"\%", "%").replace(r"\_", "_").replace(r"\--", "–").replace(r"---", "—")
    source = re.sub(r"\\[a-zA-Z]+(?:\[[^]]*\])?(?:\{([^{}]*)\})?", lambda m: m.group(1) or "", source)
    source = re.sub(r"(?m)^\s*(?:\}|\{)\s*$", "", source)
    source = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", "", source)
    source = re.sub(r"\\[{}]", "", source)
    blocks=[]
    for p in re.split(r"\n\s*\n", source):
        p=p.strip()
        if not p or p.startswith("\\"): continue
        if p.startswith("<"): blocks.append(p)
        else: blocks.append("<p>"+p+"</p>")
    return "\n".join(blocks)


def render_pdf(body: str, target: Path, title: str, css: str) -> None:
    title_block = f'<h1>{html.escape(title)}</h1>' if title else ""
    doc = f'<!doctype html><meta charset="utf-8"><title>{html.escape(title)}</title><style>{css}</style><main>{title_block}{body}</main>'
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
        f.write(doc); html_path = Path(f.name)
    try:
        with tempfile.TemporaryDirectory(prefix="episcope-chrome-") as profile:
            subprocess.run([str(CHROME), "--headless", "--no-sandbox", "--disable-gpu", "--disable-gpu-compositing", "--disable-software-rasterizer", "--no-pdf-header-footer", f"--user-data-dir={profile}", f"--print-to-pdf={target}", html_path.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        html_path.unlink(missing_ok=True)


def main():
    if not CHROME.exists(): raise SystemExit(f"Chrome not found: {CHROME}")
    slide_html = update_slides()
    slide_deck(slide_html, DOCS / "presentation.pptx")

    report_source = (DOCS / "episcope_ieee_report.tex").read_text(encoding="utf-8")
    brief_source = (DOCS / "policy_brief.tex").read_text(encoding="utf-8")
    report_main = re.sub(r"(?s)\\appendices.*?\\end\{document\}", "", report_source)
    report_html = latex_to_html(report_main)
    author_names = "<br>".join(f"{html.escape(name)} ({idno})" for name, idno in MEMBERS)
    report_html = f'<div class="authorblock">{author_names}<br>Department of Computer Science and Engineering<br>Premier University, Chattogram, Bangladesh<br>Repository: https://github.com/mdrobiulhassan/EpiScope</div>' + report_html
    brief_html = latex_to_html(brief_source)
    brief_header = '<h2>Appendix: Policy Brief for Public-Health Decision Makers</h2><h3>EpiScope: A research prototype for surveillance and preparedness</h3><p><b>Prepared by:</b> Md. Samin Osman (0222220005101042), Robiul Hassan (0222220005101043), Walid Talal (0222220005101045), and Md. Mahafujul Alam (0222220005101066).</p>'
    brief_html = brief_header + brief_html
    report_css = '@page{size:letter;margin:.55in .58in}body{font:9pt/1.24 "Times New Roman",serif;color:#111}h1{font-size:15pt;text-align:center}h2{font-size:12pt;column-span:all;margin:10pt 0 4pt}h3{font-size:10pt;margin:7pt 0 2pt}p,ul{margin:2pt 0 5pt;text-align:justify}li{margin:1pt 0}.abstract{font-size:8.5pt;text-align:justify}.pagebreak{break-before:page;column-span:all}main{column-count:2;column-gap:.24in}main>h1{column-span:all}.authorblock{column-span:all;text-align:center;font-size:8pt;line-height:1.25;margin:4pt 0 12pt}table{border-collapse:collapse;width:100%;font-size:8pt;margin:5pt 0}td{border-bottom:1px solid #aaa;padding:2pt 4pt}caption{font-weight:bold;text-align:left;margin:3pt 0}code{font-size:7pt;overflow-wrap:anywhere}'
    render_pdf(report_html + '<div class="pagebreak"></div>' + brief_html, DOCS / "episcope_ieee_report.pdf", "EpiScope: IEEE Project Report", report_css)
    brief_css = '@page{size:letter;margin:.38in .48in}body{font:7.5pt/1.1 Arial,sans-serif;color:#172b3a}h1{font-size:14pt;color:#092338;margin:0 0 4pt}h2{font-size:9.5pt;color:#087f72;margin:5pt 0 2pt;break-after:avoid}h3{font-size:8pt;color:#092338;margin:3pt 0 1pt;break-after:avoid}p,ul{margin:1pt 0 2pt;text-align:justify}li{margin:1pt 0}.briefpage{column-count:2;column-gap:.3in}.briefpage+.briefpage{break-before:page}.briefpage h1,.briefpage h2{column-span:all}main>h1{border-bottom:2px solid #12ad98;padding-bottom:3pt}'
    chunks = brief_html.replace(brief_header, "", 1).split('<div class="pagebreak"></div>')
    byline = '<p><b>Prepared by:</b> Md. Samin Osman (0222220005101042), Robiul Hassan (0222220005101043), Walid Talal (0222220005101045), and Md. Mahafujul Alam (0222220005101066).</p>'
    standalone = '<div class="briefpage"><h1>EpiScope Policy Brief</h1>' + byline + (chunks[0] if chunks else '') + '</div>'
    if len(chunks) > 1:
        standalone += '<div class="briefpage">' + chunks[1] + '</div>'
    render_pdf(standalone, DOCS / "policy_brief.pdf", "", brief_css)
    for name in ["episcope_ieee_report.pdf", "policy_brief.pdf", "presentation.pptx"]:
        print(f"{name}: {(DOCS / name).stat().st_size:,} bytes")


if __name__ == "__main__": main()
