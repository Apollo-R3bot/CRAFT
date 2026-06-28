import os
import json
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, PageBreak,
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

# ── Palette ────────────────────────────────────────────────────────────────
C_PRIMARY   = HexColor("#1591DC")
C_DARK      = HexColor("#0a1228")
C_HEADER_BG = HexColor("#0d1b3e")
C_ROW_ALT   = HexColor("#f0f6ff")
C_BORDER    = HexColor("#c8d8f0")
C_RED       = HexColor("#dc2626")
C_GREEN     = HexColor("#16a34a")
C_AMBER     = HexColor("#d97706")
C_WHITE     = HexColor("#f0f6ff")
C_BLACK     = colors.black
C_GREY      = HexColor("#64748b")

# Maps the artifact key used in SECTION_META to every possible dict key
# that marked_evidence might use (display title, file stem, raw key).
# Marked evidence keys come from self.title in ArtifactTableController
# which is set by each page controller (e.g. "History", "Downloads").
KEY_ALIASES = {
    "history":      ["history",      "History"],
    "downloads":    ["downloads",    "Downloads"],
    "cookies":      ["cookies",      "Cookies"],
    "logins":       ["logins",       "Password",    "Logins"],
    "search_terms": ["search_terms", "Search Terms", "SearchTerms"],
    "bookmarks":    ["bookmarks",    "Bookmarks"],
    "autofill":     ["autofill",     "Form Data"],
    "top_sites":    ["top_sites",    "Frequently Websites",
                     "Frequently Visited Sites"],
}

def _resolve(data, canonical_key):
    """
    Look up a DataFrame from data using any known alias for canonical_key.
    Returns an empty DataFrame if nothing matches.
    """
    for alias in KEY_ALIASES.get(canonical_key, [canonical_key]):
        if alias in data:
            val = data[alias]
            if isinstance(val, pd.DataFrame):
                return val
            # marked_evidence stores dicts from get_marked_rows()
            try:
                return pd.DataFrame(val)
            except Exception:
                pass
    return pd.DataFrame()


class ReportController:
    def __init__(self, evidence_path):
        self.evidence_path   = evidence_path
        self.marked_evidence = {}

        self.files = [
            "history.csv", "downloads.csv", "cookies.csv", "logins.csv",
            "search_terms.csv", "bookmarks.csv", "autofill.csv", "top_sites.csv",
        ]

        self.table_style = TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  C_HEADER_BG),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  C_WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_ROW_ALT]),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])

        self.case_table_style = TableStyle([
            ("FONTNAME",      (0, 0), (0, -1),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("TEXTCOLOR",     (0, 0), (0, -1),  C_PRIMARY),
            ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
            ("BACKGROUND",    (0, 0), (0, -1),  HexColor("#eef6fd")),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])

    # ── Style helpers ──────────────────────────────────────────────────

    def _styles(self):
        base = getSampleStyleSheet()
        S = {}
        S["title"]     = ParagraphStyle("CraftTitle",    parent=base["Title"],
                            textColor=C_PRIMARY, fontSize=26, leading=30, spaceAfter=4)
        S["subtitle"]  = ParagraphStyle("CraftSubtitle", parent=base["Normal"],
                            textColor=C_GREY, fontSize=10, spaceAfter=2)
        S["h1"]        = ParagraphStyle("CraftH1",       parent=base["Heading1"], textColor=C_WHITE, 
                            fontSize=13, leading=16, backColor=C_HEADER_BG, borderPad=6,
                            leftIndent=-4, rightIndent=-4, spaceBefore=14, spaceAfter=6)
        S["h2"]        = ParagraphStyle("CraftH2",       parent=base["Heading2"], textColor=C_PRIMARY, 
                            fontSize=11, leading=14, spaceBefore=10, spaceAfter=4)
        S["body"]      = ParagraphStyle("CraftBody",     parent=base["Normal"],
                            fontSize=9, leading=13, spaceAfter=4)
        S["bullet"]    = ParagraphStyle("CraftBullet",   parent=base["Normal"],
                            fontSize=9, leading=13, leftIndent=12, bulletIndent=4)
        S["cell"]      = ParagraphStyle("CraftCell",     parent=base["Normal"],
                            fontSize=7.5, leading=10, wordWrap="CJK")
        S["cell_bold_cover"] = ParagraphStyle("CraftCellBold", parent=base["Normal"],
                            fontSize=7.5, leading=10, fontName="Helvetica-Bold", wordWrap="CJK")
        S["cell_bold"] = ParagraphStyle("CraftCellBold", parent=base["Normal"], fontSize=7.5, 
                            leading=10, fontName="Helvetica-Bold",textColor=C_WHITE, wordWrap="CJK")
        S["toc_title"] = ParagraphStyle("CraftTOCTitle", parent=base["Normal"], textColor=C_PRIMARY, 
                            fontSize=13, fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=8)
        S["toc_item"]  = ParagraphStyle("CraftTOCItem",  parent=base["Normal"],
                            fontSize=9, leading=14, leftIndent=8)
        S["toc_sub"]   = ParagraphStyle("CraftTOCSub",   parent=base["Normal"],
                            fontSize=8, leading=13, leftIndent=22, textColor=C_GREY)
        S["small"]     = ParagraphStyle("CraftSmall",    parent=base["Normal"],
                            fontSize=7, textColor=C_GREY, leading=10)
        return S

    def _hr(self, color=C_PRIMARY, thickness=0.8):
        return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4)

    def _section_header(self, number, title, S):
        return Paragraph(f"&nbsp;&nbsp;{number}. {title.upper()}", S["h1"])

    def _make_table(self, df, S, max_rows=100):
        df = df.head(max_rows)
        headers = [Paragraph(str(c), S["cell_bold"]) for c in df.columns]
        rows = [[Paragraph(str(v), S["cell"]) for v in row]
                for row in df.astype(str).values.tolist()]
        page_w = A4[0] - 64
        col_w  = page_w / len(df.columns)
        t = Table([headers] + rows, colWidths=[col_w]*len(df.columns), repeatRows=1)
        t.setStyle(self.table_style)
        return t

    def _bullet(self, text, S):
        return Paragraph(f"&#8226; &nbsp;{text}", S["bullet"])

    def _browser_logo(self, browser_type, size=60):
        """Return a ReportLab Image for the browser logo, or None if not found."""
        base_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        icon_map   = {
            "chrome":  "chrome.png",
            "edge":    "edge.png",
            "firefox": "firefox.png",
            "opera":   "opera.png",
        }
        icon_file  = icon_map.get(str(browser_type).lower(), "default.png")
        icon_path  = os.path.join(base_dir, "src", "resources", "icons", icon_file)

        # Also try without the extra src/ prefix
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_dir, "resources", "icons", icon_file)

        if os.path.exists(icon_path):
            try:
                return Image(icon_path, width=size, height=size)
            except Exception:
                pass
        return None

    # ── Data loaders ───────────────────────────────────────────────────

    def get_case_information(self):
        prefs_file = os.path.join(self.evidence_path, "preferences.json")
        if not os.path.exists(prefs_file):
            return {}
        try:
            with open(prefs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("case_information", {})
        except Exception:
            return {}

    def get_machine_info(self):
        prefs_file = os.path.join(self.evidence_path, "preferences.json")
        if not os.path.exists(prefs_file):
            return {}
        try:
            with open(prefs_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def load_all_data(self):
        report_data = {}
        for file in self.files:
            path = os.path.join(self.evidence_path, file)
            key  = file.replace(".csv", "")
            if os.path.exists(path):
                try:
                    report_data[key] = pd.read_csv(path)
                except Exception:
                    report_data[key] = pd.DataFrame()
        return report_data

    # ── Page header / footer ───────────────────────────────────────────

    def add_page_header_footer(self, canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setFillColor(C_HEADER_BG)
        canvas.rect(0, h - 28, w, 28, fill=1, stroke=0)
        canvas.setFillColor(C_WHITE)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(30, h - 18, "CRAFT")
        canvas.setFont("Helvetica", 8)
        canvas.drawString(70, h - 18, "Cross Browser Artifact Forensic Tool")
        canvas.setFillColor(HexColor("#94a3b8"))
        canvas.drawRightString(w - 30, h - 18, "BROWSER FORENSIC INVESTIGATION REPORT")
        canvas.setFillColor(C_HEADER_BG)
        canvas.rect(0, 0, w, 22, fill=1, stroke=0)
        canvas.setFillColor(C_WHITE)
        canvas.drawRightString(w - 30, 7, f"Page {doc.page}")
        canvas.restoreState()

    # ── Cover page ─────────────────────────────────────────────────────
    def _cover_page(self, elements, S, prefs, case_info):
        machine      = prefs.get("machine_info", {})
        browser      = prefs.get("browser_info", {})
        browser_type = browser.get("browser_type", "")

        elements.append(Spacer(1, 30))

        # CRAFT title
        title_para = Paragraph("CRAFT", S["title"])
        sub_para   = Paragraph("Cross Browser Artifact Forensic Tool", S["subtitle"])
        elements.append(title_para)
        elements.append(sub_para)

        elements.append(Spacer(1, 4))
        elements.append(self._hr(C_PRIMARY, 1.5))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(
            "<font color='#64748b'>BROWSER FORENSIC INVESTIGATION REPORT</font>",
            S["subtitle"]
        ))
        elements.append(Spacer(1, 20))

        generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cover_data = [
            ["Report Generated On", generated_date],
            ["Case Number",         case_info.get("case_number",    "—")],
            ["Evidence Number",     case_info.get("evidence_number","—")],
            ["Examiner",            case_info.get("examiner_name",  "—")],
            ["Browser Examined",    f"{browser_type} {browser.get('browser_version','')}".strip()],
            ["User Profile",        browser.get("profile_user",     "—")],
            ["Hostname",            machine.get("hostname",          "—")],
            ["Username",            machine.get("username",          "—")],
            ["Operating System",    machine.get("os_version",        machine.get("os_release","—"))],
        ]
        wrapped = [
            [Paragraph(r[0], S["cell_bold_cover"]), Paragraph(str(r[1]), S["cell"])]
            for r in cover_data
        ]
        t = Table(wrapped, colWidths=[140, 320], hAlign="LEFT")
        t.setStyle(self.case_table_style)
        elements.append(t)

        notes = case_info.get("notes", "")
        if notes:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Case Description", S["h2"]))
            elements.append(Paragraph(str(notes), S["body"]))

        elements.append(Spacer(1, 16))
        elements.append(Paragraph(
            "Investigation Objective: Aim of this investigation is to identify and analyze browser artifacts recovered "
            "from the acquired evidence source and determine significant user activity "
            "relevant to the investigation.",
            S["body"]
        ))
        elements.append(PageBreak())

    # ── Table of Contents ──────────────────────────────────────────────
    def _table_of_contents(self, elements, S, data):
        elements.append(Paragraph("Table of Contents", S["toc_title"]))
        elements.append(self._hr(C_PRIMARY, 0.5))
        elements.append(Spacer(1, 6))

        TOC = [
            ("1.", "Cover Page",        []),
            ("2.", "Introduction",      []),
            ("3.", "Executive Summary", []),
            ("4.", "Artifact Analysis", []),
            ("5.", "Timeline Analysis",  []),
            ("6.", "Conclusion",         []),
            ("7.", "Examiner Notes",     []),
        ]

        for num, title, subs in TOC:
            # Mark sections with no data in grey
            has_data = True
            if num in ("4.",):
                has_data = any(
                    not _resolve(data, k).empty
                    for k in KEY_ALIASES
                )

            color = "#0d1b3e" if has_data else "#94a3b8"
            elements.append(Paragraph(
                f"<font color='{color}'><b>{num}</b>&nbsp;&nbsp;{title}</font>",
                S["toc_item"]
            ))
            for sub_num, sub_title in subs:
                key = {
                    "4.1": "history",    "4.2": "downloads",
                    "4.3": "search_terms","4.4": "autofill",
                    "4.5": "cookies",    "4.6": "logins",
                    "4.7": "bookmarks",  "4.8": "top_sites",
                }.get(sub_num, "")
                sub_has = not _resolve(data, key).empty if key else True
                sub_color = "#1591DC" if sub_has else "#94a3b8"
                elements.append(Paragraph(
                    f"<font color='{sub_color}'>{sub_num}&nbsp;&nbsp;{sub_title}</font>",
                    S["toc_sub"]
                ))

        elements.append(PageBreak())

    # ── Section 2: Introduction ────────────────────────────────────────
    def _section_introduction(self, elements, S):
        elements.append(self._section_header(2, "Introduction", S))
        elements.append(Paragraph(
            "This report presents the results of a browser forensic examination performed "
            "using the CRAFT (Cross Browser Artifact Forensic Tool) platform.", S["body"]))
        elements.append(Paragraph(
            "The examination involved the acquisition, parsing, analysis, and interpretation "
            "of browser artifacts recovered from the selected user profile. Browser artifacts "
            "including browsing history, downloads, autofill records, search terms, bookmarks, "
            "cookies, session information, and other available web artifacts were examined.",
            S["body"]))
        elements.append(Paragraph(
            "All findings contained within this report are based solely on recovered digital "
            "artifacts and should be considered in conjunction with other available "
            "investigative evidence.", S["body"]))
        elements.append(Spacer(1, 8))

    # ── Section 3: Executive Summary ──────────────────────────────────
    def _section_executive_summary(self, elements, S, data):
        elements.append(self._section_header(3, "Executive Summary", S))

        total = sum(
            len(_resolve(data, k))
            for k in KEY_ALIASES
        )
        elements.append(Paragraph(
            f"A total of <b>{total}</b> browser artifacts were recovered and analyzed.",
            S["body"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Summary of Findings:", S["h2"]))

        summary_rows = [[
            Paragraph("Artifact Type",     S["cell_bold"]),
            Paragraph("Records Recovered", S["cell_bold"]),
        ]]
        for canonical, aliases in KEY_ALIASES.items():
            df    = _resolve(data, canonical)
            count = len(df) if not df.empty else 0
            summary_rows.append([
                Paragraph(canonical.replace("_", " ").title(), S["cell"]),
                Paragraph(str(count), S["cell"]),
            ])

        t = Table(summary_rows, colWidths=[200, 150], hAlign="LEFT", repeatRows=1)
        t.setStyle(self.table_style)
        elements.append(t)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Key Observations:", S["h2"]))
        for obs in [
            "Browsing history records recovered and analyzed.",
            "Download activity detected and examined.",
            "Search terms extracted and categorized.",
            "Saved login credentials recovered.",
            "Autofill / form-entry data recovered.",
            "Cookie records analyzed.",
            "Bookmarks extracted.",
        ]:
            elements.append(self._bullet(obs, S))
        elements.append(Spacer(1, 8))

    # ── Section 4: Artifact Analysis ──────────────────────────────────
    def _section_artifact_analysis(self, elements, S, data):
        elements.append(self._section_header(4, "Artifact Analysis", S))

        SECTION_META = [
            ("history",      "4.1", "History Analysis",              self._history_observations),
            ("downloads",    "4.2", "Download Analysis",             self._download_observations),
            ("search_terms", "4.3", "Search Term Analysis",          self._search_observations),
            ("autofill",     "4.4", "Autofill / Form Data Analysis", self._autofill_observations),
            ("cookies",      "4.5", "Cookie Analysis",               self._cookie_observations),
            ("logins",       "4.6", "Saved Login Analysis",          self._logins_observations),
            ("bookmarks",    "4.7", "Bookmark Analysis",             self._bookmarks_observations),
            ("top_sites",    "4.8", "Frequently Visited Sites",      None),
        ]

        for canonical, num, title, obs_fn in SECTION_META:
            # Resolve using alias table — works for both full and marked export
            df = _resolve(data, canonical)

            elements.append(Paragraph(f"{num} {title}", S["h2"]))

            if df.empty:
                elements.append(Paragraph("No data recovered.", S["body"]))
                elements.append(Spacer(1, 8))
                continue

            elements.append(Paragraph(
                f"Recovered {canonical.replace('_',' ')} records ({len(df)} total):",
                S["body"]))
            elements.append(self._make_table(df, S, max_rows=50))

            if obs_fn:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph("Observations:", S["h2"]))
                obs_fn(elements, S, df)

            elements.append(Spacer(1, 12))

    # ── Per-section observations ───────────────────────────────────────
    def _history_observations(self, elements, S, df):
        total   = len(df)
        active  = len(df[df["Status"] == "Active"])  if "Status" in df.columns else "—"
        deleted = len(df[df["Status"] == "Deleted"]) if "Status" in df.columns else "—"
        elements.append(self._bullet(f"Total URL visits: {total}", S))
        elements.append(self._bullet(f"Active records: {active}", S))
        elements.append(self._bullet(f"Deleted / gap records detected: {deleted}", S))
        if "URL" in df.columns:
            try:
                from urllib.parse import urlparse
                domains = df["URL"].dropna().apply(
                    lambda u: urlparse(str(u)).netloc.replace("www.", ""))
                for domain, count in domains.value_counts().head(3).items():
                    elements.append(Paragraph(
                        f"&nbsp;&nbsp;&nbsp;&nbsp;– {domain} ({count} visits)", S["bullet"]))
            except Exception:
                pass
        if "Visit Time" in df.columns:
            try:
                times = pd.to_datetime(df["Visit Time"], errors="coerce").dropna()
                if not times.empty:
                    elements.append(self._bullet(f"Earliest visit: {times.min()}", S))
                    elements.append(self._bullet(f"Latest visit:   {times.max()}", S))
            except Exception:
                pass

    def _download_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total downloads: {len(df)}", S))
        if "Status" in df.columns:
            for status in ["COMPLETE", "CANCELLED", "INTERRUPTED"]:
                count = len(df[df["Status"] == status])
                if count:
                    elements.append(self._bullet(f"{status}: {count}", S))
        if "File Name" in df.columns:
            exe = df["File Name"].dropna().astype(str).str.lower()
            n   = exe.str.endswith((".exe",".msi",".bat",".ps1")).sum()
            if n:
                elements.append(self._bullet(f"Executable files identified: {n}", S))

    def _search_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total search queries: {len(df)}", S))
        if "Term" in df.columns:
            for term, count in df["Term"].value_counts().head(5).items():
                elements.append(Paragraph(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;– \"{term}\" ({count}x)", S["bullet"]))
        if "Domain" in df.columns:
            for d, c in df["Domain"].value_counts().head(3).items():
                elements.append(Paragraph(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;– {d} ({c} queries)", S["bullet"]))

    def _autofill_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total autofill entries: {len(df)}", S))
        if "Field Name" in df.columns:
            elements.append(self._bullet(
                f"Unique form fields: {df['Field Name'].dropna().nunique()}", S))
        if "Value" in df.columns:
            emails = df["Value"].dropna().astype(str).str.contains(r"@.*\.", regex=True).sum()
            if emails:
                elements.append(self._bullet(f"Email addresses identified: {emails}", S))

    def _cookie_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total cookies: {len(df)}", S))
        if "Host" in df.columns:
            elements.append(self._bullet(f"Unique hosts: {df['Host'].nunique()}", S))

    def _logins_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total saved credentials: {len(df)}", S))
        if "Origin URL" in df.columns:
            elements.append(self._bullet(f"Unique sites: {df['Origin URL'].nunique()}", S))

    def _bookmarks_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total bookmarks: {len(df)}", S))

    # ── Section 5: Timeline ────────────────────────────────────────────
    def _section_timeline(self, elements, S, data):
        elements.append(self._section_header(5, "Timeline Analysis", S))
        elements.append(Paragraph(
            "Chronological reconstruction of recovered browser activity.", S["body"]))
        elements.append(Spacer(1, 6))

        timeline_rows = []
        for canonical, time_col, type_label, detail_col in [
            ("history",      "Visit Time", "History",  "URL"),
            ("downloads",    "Start Time", "Download", "File Name"),
            ("search_terms", "Visit Time", "Search",   "Term"),
        ]:
            df = _resolve(data, canonical)
            if df.empty or time_col not in df.columns:
                continue
            for _, row in df.head(30).iterrows():
                timeline_rows.append({
                    "time":   str(row.get(time_col, "")),
                    "type":   type_label,
                    "detail": str(row.get(detail_col, ""))[:80],
                })

        if timeline_rows:
            timeline_rows.sort(key=lambda r: r["time"])
            headers = [
                Paragraph("Date &amp; Time", S["cell_bold"]),
                Paragraph("Artifact Type",   S["cell_bold"]),
                Paragraph("Activity",         S["cell_bold"]),
            ]
            rows = [[
                Paragraph(r["time"],   S["cell"]),
                Paragraph(r["type"],   S["cell"]),
                Paragraph(r["detail"], S["cell"]),
            ] for r in timeline_rows]
            t = Table([headers] + rows, colWidths=[130, 80, 270], repeatRows=1)
            t.setStyle(self.table_style)
            elements.append(t)
        else:
            elements.append(Paragraph(
                "Insufficient timestamp data to reconstruct timeline.", S["body"]))

        elements.append(Spacer(1, 8))

    # ── Section 6 + 7: Conclusion + Notes ─────────────────────────────
    def _section_conclusion(self, elements, S, data, case_info):
        elements.append(self._section_header(6, "Conclusion", S))
        total = sum(len(_resolve(data, k)) for k in KEY_ALIASES)
        elements.append(Paragraph(
            f"This examination successfully recovered and analyzed <b>{total}</b> browser "
            "artifacts from the acquired evidence source.", S["body"]))
        elements.append(Paragraph(
            "Timeline reconstruction established a chronological sequence of events. "
            "All findings are based solely on recovered digital evidence and should be "
            "interpreted alongside other available investigative information.", S["body"]))
        elements.append(Spacer(1, 6))

        notes = case_info.get("notes", "").strip()
        elements.append(self._section_header(7, "Examiner Notes", S))
        elements.append(Paragraph(notes or "No examiner notes recorded.", S["body"]))


    # ── Main PDF export ────────────────────────────────────────────────
    def export_full_pdf(self, output_file, marked_data=None):
        # Normalise: marked_evidence values may be DataFrames or list-of-dicts
        if marked_data:
            data = {}
            for k, v in marked_data.items():
                data[k] = pd.DataFrame(v) if not isinstance(v, pd.DataFrame) else v
        else:
            data = self.load_all_data()

        prefs     = self.get_machine_info()
        case_info = prefs.get("case_information", {})
        S         = self._styles()

        pdf = SimpleDocTemplate(
            output_file, pagesize=A4,
            leftMargin=32, rightMargin=32, topMargin=40, bottomMargin=32,
        )
        elements = []

        self._cover_page(elements, S, prefs, case_info)
        self._table_of_contents(elements, S, data)        # ← new
        self._section_introduction(elements, S)
        self._section_executive_summary(elements, S, data)
        elements.append(PageBreak())
        self._section_artifact_analysis(elements, S, data)
        elements.append(PageBreak())
        self._section_timeline(elements, S, data)
        elements.append(PageBreak())
        self._section_conclusion(elements, S, data, case_info)

        pdf.build(elements,
                  onFirstPage=self.add_page_header_footer,
                  onLaterPages=self.add_page_header_footer)

    # ── JSON / CSV exports ─────────────────────────────────────────────
    def export_full_json(self, output_file):
        data  = self.load_all_data()
        final = {k: df.to_dict(orient="records") for k, df in data.items()}
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final, f, indent=4, ensure_ascii=False)

    def export_full_csv(self, output_file):
        data     = self.load_all_data()
        combined = pd.DataFrame()
        for section, df in data.items():
            if not df.empty:
                df = df.copy()
                df.insert(0, "Artifact Type", section)
                combined = pd.concat([combined, df], ignore_index=True)
        combined.to_csv(output_file, index=False, encoding="utf-8-sig")

    def export_marked_csv(self, output_file, marked_data):
        combined = pd.DataFrame()
        for section, v in marked_data.items():
            df = pd.DataFrame(v) if not isinstance(v, pd.DataFrame) else v
            if not df.empty:
                df = df.copy()
                df.insert(0, "Artifact Type", section)
                combined = pd.concat([combined, df], ignore_index=True)
        combined.to_csv(output_file, index=False, encoding="utf-8-sig")

    def artifact_summary(self, data):
        summary_data = [["Artefact Type", "Findings"]]
        for canonical in KEY_ALIASES:
            df = _resolve(data, canonical)
            summary_data.append([
                canonical.replace("_", " ").title(),
                str(len(df)) if not df.empty else "0",
            ])
        t = Table(summary_data, colWidths=[120, 250], repeatRows=1, hAlign="LEFT")
        t.setStyle(self.table_style)
        return t