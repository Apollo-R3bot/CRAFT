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


class ReportController:
    def __init__(self, evidence_path):
        self.evidence_path  = evidence_path
        self.marked_evidence = {}

        self.files = [
            "history.csv",
            "downloads.csv",
            "cookies.csv",
            "logins.csv",
            "search_terms.csv",
            "bookmarks.csv",
            "autofill.csv",
            "sessions.csv",
            "top_sites.csv",
        ]

        # ── Shared table styles ────────────────────────────────────────
        self.table_style = TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0),  C_HEADER_BG),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  C_WHITE),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 8),
            ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),   [C_WHITE, C_ROW_ALT]),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ])

        self.case_table_style = TableStyle([
            ("FONTNAME",     (0, 0), (0, -1),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("TEXTCOLOR",    (0, 0), (0, -1),  C_PRIMARY),
            ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
            ("BACKGROUND",   (0, 0), (0, -1),  HexColor("#eef6fd")),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ])

    # ── Helpers ────────────────────────────────────────────────────────

    def _styles(self):
        base = getSampleStyleSheet()
        S = {}

        S["title"] = ParagraphStyle(
            "CraftTitle", parent=base["Title"],
            textColor=C_PRIMARY, fontSize=26, leading=30, spaceAfter=4,
        )
        S["subtitle"] = ParagraphStyle(
            "CraftSubtitle", parent=base["Normal"],
            textColor=C_GREY, fontSize=10, spaceAfter=2,
        )
        S["h1"] = ParagraphStyle(
            "CraftH1", parent=base["Heading1"],
            textColor=C_WHITE, fontSize=13, leading=16,
            backColor=C_HEADER_BG, borderPad=6,
            leftIndent=-4, rightIndent=-4,
            spaceBefore=14, spaceAfter=6,
        )
        S["h2"] = ParagraphStyle(
            "CraftH2", parent=base["Heading2"],
            textColor=C_PRIMARY, fontSize=11, leading=14,
            spaceBefore=10, spaceAfter=4,
        )
        S["body"] = ParagraphStyle(
            "CraftBody", parent=base["Normal"],
            fontSize=9, leading=13, spaceAfter=4,
        )
        S["bullet"] = ParagraphStyle(
            "CraftBullet", parent=base["Normal"],
            fontSize=9, leading=13, leftIndent=12, bulletIndent=4,
        )
        S["cell"] = ParagraphStyle(
            "CraftCell", parent=base["Normal"],
            fontSize=7.5, leading=10, wordWrap="CJK",
        )
        S["cell_bold"] = ParagraphStyle(
            "CraftCellBold", parent=base["Normal"],
            fontSize=7.5, leading=10, fontName="Helvetica-Bold",
            wordWrap="CJK",
        )
        S["label"] = ParagraphStyle(
            "CraftLabel", parent=base["Normal"],
            fontSize=8, textColor=C_GREY,
        )
        S["small"] = ParagraphStyle(
            "CraftSmall", parent=base["Normal"],
            fontSize=7, textColor=C_GREY, leading=10,
        )
        return S

    def _hr(self, color=C_PRIMARY, thickness=0.8):
        return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4)

    def _section_header(self, number, title, S):
        """Dark band section header matching the template."""
        return Paragraph(f"&nbsp;&nbsp;{number}. {title.upper()}", S["h1"])

    def _make_table(self, df, S, max_rows=100):
        """Wrap a DataFrame into a styled ReportLab Table."""
        df = df.head(max_rows)
        headers = [Paragraph(str(c), S["cell_bold"]) for c in df.columns]
        rows = [
            [Paragraph(str(v), S["cell"]) for v in row]
            for row in df.astype(str).values.tolist()
        ]
        page_w = A4[0] - 64          # usable width (32mm margin each side)
        col_w  = page_w / len(df.columns)
        t = Table([headers] + rows, colWidths=[col_w]*len(df.columns), repeatRows=1)
        t.setStyle(self.table_style)
        return t

    def _bullet(self, text, S):
        return Paragraph(f"&#8226; &nbsp;{text}", S["bullet"])

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
                data = json.load(f)
            return data
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

        # Top bar
        canvas.setFillColor(C_HEADER_BG)
        canvas.rect(0, h - 58, w, 58, fill=1, stroke=0)
        canvas.setFillColor(C_WHITE)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(30, h - 18, "CRAFT")
        canvas.setFont("Helvetica", 8)
        canvas.drawString(70, h - 18, "Cross Browser Artifact Forensic Tool")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(HexColor("#94a3b8"))
        canvas.drawRightString(w - 30, h - 18, "BROWSER FORENSIC INVESTIGATION REPORT")

        # Bottom bar
        canvas.setFillColor(C_HEADER_BG)
        canvas.rect(0, 0, w, 22, fill=1, stroke=0)
        canvas.setFillColor(C_GREY)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(30, 7, "CONFIDENTIAL — FOR OFFICIAL USE ONLY")
        canvas.setFillColor(C_WHITE)
        canvas.drawRightString(w - 30, 7, f"Page {doc.page}")

        canvas.restoreState()

    # ── Cover page ─────────────────────────────────────────────────────
    def _cover_page(self, elements, S, prefs, case_info):
        machine = prefs.get("machine_info", {})
        browser = prefs.get("browser_info", {})

        elements.append(Spacer(1, 40))
        elements.append(Paragraph("CRAFT", S["title"]))
        elements.append(Paragraph("Cross Browser Artifact Forensic Tool", S["subtitle"]))
        elements.append(Spacer(1, 4))
        elements.append(self._hr(C_PRIMARY, 1.5))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(
            "<font color='#64748b'>BROWSER FORENSIC INVESTIGATION REPORT</font>",
            S["subtitle"]
        ))
        elements.append(Spacer(1, 30))
        generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Two-column cover info box
        cover_data = [
            ["Report Generated On", generated_date],
            ["Case Number",         case_info.get("case_number", "—")],
            ["Evidence Number",     case_info.get("evidence_number", "—")],
            ["Examiner",            case_info.get("examiner_name", "—")],
            ["Browser Examined",    browser.get("browser_type", "—") + " " + browser.get("browser_version", "—")],
            ["User Profile",        browser.get("profile_user", "—")],
            ["Hostname",            machine.get("hostname", "—")],
            ["Username",            machine.get("username", "—")],
            ["Operating System",    machine.get("os_version", "—")],
        ]

        wrapped = [
            [Paragraph(r[0], S["cell_bold"]), Paragraph(str(r[1]), S["cell"])]
            for r in cover_data
        ]
        t = Table(wrapped, colWidths=[140, 320], hAlign="LEFT")
        t.setStyle(self.case_table_style)
        elements.append(t)

        # Case description / notes
        notes = case_info.get("notes", "")
        if notes:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Case Description", S["h2"]))
            elements.append(Paragraph(str(notes), S["body"]))

        elements.append(Spacer(1, 16))
        elements.append(Paragraph(
            "Investigation Objective: To identify and analyze browser artifacts recovered "
            "from the acquired evidence source and determine significant user activity "
            "relevant to the investigation.",
            S["body"]
        ))
        elements.append(PageBreak())

    # ── Section 2: Introduction ────────────────────────────────────────

    def _section_introduction(self, elements, S):
        elements.append(self._section_header(2, "Introduction", S))
        elements.append(Paragraph(
            "This report presents the results of a browser forensic examination performed "
            "using the CRAFT (Cross Browser Artifact Forensic Tool) platform.",
            S["body"]
        ))
        elements.append(Paragraph(
            "The examination involved the acquisition, parsing, analysis, and interpretation "
            "of browser artifacts recovered from the selected user profile. Browser artifacts "
            "including browsing history, downloads, autofill records, search terms, bookmarks, "
            "cookies, session information, and other available web artifacts were examined.",
            S["body"]
        ))
        elements.append(Paragraph(
            "All findings contained within this report are based solely on recovered digital "
            "artifacts and should be considered in conjunction with other available investigative evidence.",
            S["body"]
        ))
        elements.append(Spacer(1, 8))

    # ── Section 3: Executive Summary ──────────────────────────────────

    def _section_executive_summary(self, elements, S, data):
        elements.append(self._section_header(3, "Executive Summary", S))

        total = sum(len(df) for df in data.values())
        elements.append(Paragraph(
            f"A total of <b>{total}</b> browser artifacts were recovered and analyzed.",
            S["body"]
        ))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Summary of Findings:", S["h2"]))

        summary_rows = [
            [Paragraph("Artifact Type", S["cell_bold"]),
             Paragraph("Records Recovered", S["cell_bold"])],
        ]
        for section, df in data.items():
            count = len(df) if not df.empty else 0
            summary_rows.append([
                Paragraph(section.replace("_", " ").title(), S["cell"]),
                Paragraph(str(count), S["cell"]),
            ])

        t = Table(summary_rows, colWidths=[200, 150], hAlign="LEFT", repeatRows=1)
        t.setStyle(self.table_style)
        elements.append(t)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Key Observations:", S["h2"]))
        obs = [
            "Browsing history records recovered and analyzed.",
            "Download activity detected and examined.",
            "Search terms extracted and categorized.",
            "Saved login credentials recovered.",
            "Autofill / form-entry data recovered.",
            "Cookie records analyzed.",
            "Bookmarks extracted.",
        ]
        for o in obs:
            elements.append(self._bullet(o, S))
        elements.append(Spacer(1, 8))

    # ── Section 4: Artifact Analysis ──────────────────────────────────

    def _section_artifact_analysis(self, elements, S, data):
        elements.append(self._section_header(4, "Artifact Analysis", S))

        SECTION_META = {
            "history": {
                "num": "4.1", "title": "History Analysis",
                "obs": self._history_observations,
            },
            "downloads": {
                "num": "4.2", "title": "Download Analysis",
                "obs": self._download_observations,
            },
            "search_terms": {
                "num": "4.3", "title": "Search Term Analysis",
                "obs": self._search_observations,
            },
            "autofill": {
                "num": "4.4", "title": "Autofill / Form Data Analysis",
                "obs": self._autofill_observations,
            },
            "cookies": {
                "num": "4.5", "title": "Cookie Analysis",
                "obs": self._cookie_observations,
            },
            "logins": {
                "num": "4.6", "title": "Saved Login Analysis",
                "obs": self._logins_observations,
            },
            "bookmarks": {
                "num": "4.7", "title": "Bookmark Analysis",
                "obs": self._bookmarks_observations,
            },
            "top_sites": {
                "num": "4.8", "title": "Frequently Visited Sites",
                "obs": None,
            },
        }

        for key, meta in SECTION_META.items():
            df = data.get(key, pd.DataFrame())
            elements.append(Paragraph(
                f"{meta['num']} {meta['title']}", S["h2"]
            ))

            if df.empty:
                elements.append(Paragraph("No data recovered.", S["body"]))
                elements.append(Spacer(1, 8))
                continue

            elements.append(Paragraph(
                f"Recovered {key.replace('_',' ')} records ({len(df)} total):",
                S["body"]
            ))
            elements.append(self._make_table(df, S, max_rows=50))

            if meta["obs"]:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph("Observations:", S["h2"]))
                meta["obs"](elements, S, df)

            elements.append(Spacer(1, 12))

    # ── Per-section observations ───────────────────────────────────────

    def _history_observations(self, elements, S, df):
        total = len(df)
        active  = len(df[df.get("Status", pd.Series()) == "Active"]) if "Status" in df.columns else "—"
        deleted = len(df[df.get("Status", pd.Series()) == "Deleted"]) if "Status" in df.columns else "—"

        elements.append(self._bullet(f"Total URL visits: {total}", S))
        elements.append(self._bullet(f"Active records: {active}", S))
        elements.append(self._bullet(f"Deleted / gap records detected: {deleted}", S))

        if "URL" in df.columns:
            try:
                from urllib.parse import urlparse
                domains = df["URL"].dropna().apply(
                    lambda u: urlparse(str(u)).netloc.replace("www.", "")
                )
                top = domains.value_counts().head(3)
                elements.append(self._bullet("Most visited domains:", S))
                for domain, count in top.items():
                    elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;– {domain} ({count} visits)", S["bullet"]))
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
            exes = df["File Name"].dropna().astype(str)
            exe_count = exes.str.lower().str.endswith((".exe", ".msi", ".bat", ".ps1")).sum()
            if exe_count:
                elements.append(self._bullet(
                    f"Executable files identified: {exe_count}", S
                ))

        if "Size" in df.columns:
            elements.append(self._bullet(
                f"Files downloaded: {df['File Name'].dropna().nunique() if 'File Name' in df.columns else len(df)}",
                S
            ))

    def _search_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total search queries: {len(df)}", S))
        if "Term" in df.columns:
            top = df["Term"].value_counts().head(5)
            if not top.empty:
                elements.append(self._bullet("Frequently occurring search terms:", S))
                for term, count in top.items():
                    elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;– \"{term}\" ({count}x)", S["bullet"]))
        if "Domain" in df.columns:
            top_d = df["Domain"].value_counts().head(3)
            elements.append(self._bullet("Search engines used:", S))
            for d, c in top_d.items():
                elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;– {d} ({c} queries)", S["bullet"]))

    def _autofill_observations(self, elements, S, df):
        elements.append(self._bullet(f"Total autofill entries: {len(df)}", S))
        if "Field Name" in df.columns:
            fields = df["Field Name"].dropna().unique()
            elements.append(self._bullet(f"Unique form fields: {len(fields)}", S))
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
            "Chronological reconstruction of recovered browser activity across all artifact types.",
            S["body"]
        ))
        elements.append(Spacer(1, 6))

        timeline_rows = []

        # Pull timestamped rows from history and downloads
        for key, time_col, type_label, detail_col in [
            ("history",   "Visit Time",  "History",  "URL"),
            ("downloads", "Start Time",  "Download", "File Name"),
            ("search_terms", "Visit Time", "Search", "Term"),
        ]:
            df = data.get(key, pd.DataFrame())
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
                Paragraph("Artifact Type",  S["cell_bold"]),
                Paragraph("Activity",        S["cell_bold"]),
            ]
            rows = [
                [
                    Paragraph(r["time"],   S["cell"]),
                    Paragraph(r["type"],   S["cell"]),
                    Paragraph(r["detail"], S["cell"]),
                ]
                for r in timeline_rows
            ]
            t = Table([headers] + rows, colWidths=[130, 80, 270], repeatRows=1)
            t.setStyle(self.table_style)
            elements.append(t)
        else:
            elements.append(Paragraph("Insufficient timestamp data to reconstruct timeline.", S["body"]))

        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            "The recovered artifacts were ordered chronologically to establish the progression "
            "of browser activity and identify relationships between searches, website visits, "
            "downloads, and user interactions.",
            S["body"]
        ))

    # ── Section 6: Conclusion ──────────────────────────────────────────

    def _section_conclusion(self, elements, S, data, case_info):
        elements.append(self._section_header(6, "Conclusion", S))
        total = sum(len(df) for df in data.values())
        elements.append(Paragraph(
            f"This examination successfully recovered and analyzed <b>{total}</b> browser "
            "artifacts from the acquired evidence source.",
            S["body"]
        ))
        elements.append(Paragraph(
            "The analysis identified browsing history records, downloads, autofill entries, "
            "saved credentials, cookies, bookmarks, and additional browser artifacts which were "
            "used to reconstruct user activity.",
            S["body"]
        ))
        elements.append(Paragraph(
            "Timeline reconstruction established a chronological sequence of events. "
            "All findings contained within this report are based solely on recovered digital "
            "evidence and should be interpreted alongside other available investigative information.",
            S["body"]
        ))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<i>No conclusions regarding intent, motive, or criminal conduct should be "
            "inferred solely from browser artifacts.</i>",
            S["body"]
        ))
        elements.append(Spacer(1, 12))

        # Examiner notes
        notes = case_info.get("notes", "").strip()
        elements.append(self._section_header(7, "Examiner Notes", S))
        elements.append(Paragraph(notes if notes else "No examiner notes recorded.", S["body"]))
        elements.append(Spacer(1, 10))

        # End of report
        elements.append(self._hr(C_PRIMARY))
        elements.append(Paragraph(
            "<font color='#64748b'>END OF REPORT — CRAFT Cross Browser Artifact Forensic Tool</font>",
            S["small"]
        ))

    # ── Main export ────────────────────────────────────────────────────

    def export_full_pdf(self, output_file, marked_data=None):
        data      = marked_data if marked_data else self.load_all_data()
        prefs     = self.get_machine_info()
        case_info = prefs.get("case_information", {})
        S         = self._styles()

        pdf = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            leftMargin=32,
            rightMargin=32,
            topMargin=40,
            bottomMargin=32,
        )

        elements = []

        # ── 1. Cover page ─────────────────────────────────────────────
        self._cover_page(elements, S, prefs, case_info)

        # ── 2. Introduction ───────────────────────────────────────────
        self._section_introduction(elements, S)

        # ── 3. Executive Summary ──────────────────────────────────────
        self._section_executive_summary(elements, S, data)
        elements.append(PageBreak())

        # ── 4. Artifact Analysis ──────────────────────────────────────
        self._section_artifact_analysis(elements, S, data)
        elements.append(PageBreak())

        # ── 5. Timeline ───────────────────────────────────────────────
        self._section_timeline(elements, S, data)
        elements.append(PageBreak())

        # ── 6 & 7. Conclusion + Examiner Notes ────────────────────────
        self._section_conclusion(elements, S, data, case_info)

        pdf.build(
            elements,
            onFirstPage=self.add_page_header_footer,
            onLaterPages=self.add_page_header_footer,
        )

    # ── JSON / CSV exports (unchanged) ────────────────────────────────

    def export_full_json(self, output_file):
        data = self.load_all_data()
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

    def artifact_summary(self, data):
        """Legacy helper kept for backward compatibility."""
        summary_data = [["Artefact Type", "Findings"]]
        for section, df in data.items():
            summary_data.append([
                section.replace("_", " ").title(),
                str(len(df.index)) if not df.empty else "0",
            ])
        t = Table(summary_data, colWidths=[120, 250], repeatRows=1, hAlign="LEFT")
        t.setStyle(self.table_style)
        return t