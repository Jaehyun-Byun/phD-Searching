"""Build the weekly report (Markdown + Excel) from data/jobs.json.

Usage: python scripts/build_report.py [YYYY-MM-DD]   (default: today in KST; the week ends on this date)
Writes reports/YYYY-Www.md and reports/YYYY-Www.xlsx
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))
REGIONS = [("Korea", "한국"), ("Europe", "유럽"), ("USA", "미국"), ("Asia", "아시아"), ("Other", "그 외")]
STARS = {3: "★★★", 2: "★★", 1: "★"}


def fit_str(j):
    try:
        return STARS.get(int(j.get("fit")), "")
    except (TypeError, ValueError):
        return ""


def esc(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def md_table(rows, with_region=False):
    if not rows:
        return "_없음_\n"
    head = (["지역"] if with_region else []) + ["적합", "유형", "포지션", "기관", "국가", "분야", "마감", "링크"]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for j in rows:
        cells = ([dict(REGIONS)[j["region"]]] if with_region else []) + [
            fit_str(j), j["position_type"], esc(j["title"]), esc(j["institution"]), esc(j.get("country")),
            esc(j.get("field")), j.get("deadline") or "-", f"[공고]({j['url']})" if j.get("url") else "-"]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def sort_key(j):
    try:
        fit = -int(j.get("fit") or 0)
    except (TypeError, ValueError):
        fit = 0
    return (fit, j.get("deadline") or "9999", j["institution"])


def main():
    end = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.now(KST).date()
    start = end - timedelta(days=6)
    iso = end.isocalendar()
    tag = f"{iso.year}-W{iso.week:02d}"
    jobs = json.loads((ROOT / "data" / "jobs.json").read_text(encoding="utf-8"))
    ref = end.isoformat()
    open_jobs = [j for j in jobs if not (j.get("deadline", "")[:4].isdigit() and j["deadline"] < ref)]
    new = [j for j in open_jobs if start.isoformat() <= j["first_seen"] <= ref]
    soon_limit = (end + timedelta(days=21)).isoformat()
    soon = sorted([j for j in open_jobs if j.get("deadline", "")[:4].isdigit() and j["deadline"] <= soon_limit],
                  key=lambda j: j["deadline"])

    lines = [f"# 주간 구직 리포트 {tag} ({start} ~ {end})", "",
             "## 이번 주 요약", "",
             f"- 신규 공고 **{len(new)}건** / 진행 중인 전체 공고 {len(open_jobs)}건 / 3주 내 마감 {len(soon)}건",
             "- 지역별 신규: " + ", ".join(f"{ko} {sum(j['region'] == r for j in new)}" for r, ko in REGIONS), ""]
    for r, ko in REGIONS:
        rows = sorted([j for j in new if j["region"] == r], key=sort_key)
        lines += [f"## {ko} ({r}) — 신규 {len(rows)}건", "", md_table(rows)]
        for j in rows:
            if j.get("summary"):
                lines.append(f"- **{esc(j['institution'])}** — {esc(j['title'])}: {esc(j['summary'])}")
        lines.append("")
    lines += ["## ⏰ 3주 내 마감 (전체)", "", md_table(soon, with_region=True)]

    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{tag}.md").write_text("\n".join(lines), encoding="utf-8")
    write_xlsx(out_dir / f"{tag}.xlsx", new, open_jobs, soon)
    print(f"wrote reports/{tag}.md and reports/{tag}.xlsx (new={len(new)}, open={len(open_jobs)})")


def write_xlsx(path, new, open_jobs, soon):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "openpyxl"])
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill

    cols = [("지역", "region", 8), ("적합", None, 7), ("유형", "position_type", 15), ("포지션", "title", 45),
            ("기관", "institution", 30), ("학과/부서", "department", 25), ("국가", "country", 14),
            ("분야", "field", 12), ("마감", "deadline", 11), ("요약", "summary", 50), ("링크", "url", 40),
            ("출처", "source", 14), ("최초 발견", "first_seen", 11), ("지원 여부", None, 10), ("메모", None, 25)]
    wb = Workbook()
    wb.remove(wb.active)

    def sheet(name, rows):
        ws = wb.create_sheet(name)
        ws.append([c[0] for c in cols])
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="3B4A6B")
        for j in sorted(rows, key=sort_key):
            ws.append([dict(REGIONS)[j["region"]] if k == "region" else fit_str(j) if h == "적합"
                       else (j.get(k) or "") if k else "" for h, k, _ in cols])
            link = ws.cell(row=ws.max_row, column=11)
            if link.value:
                link.hyperlink = link.value
                link.font = Font(color="0563C1", underline="single")
        for i, (_, _, w) in enumerate(cols, 1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    sheet("이번주 신규", new)
    sheet("마감 임박", soon)
    for r, ko in REGIONS:
        sheet(f"{ko} 전체", [j for j in open_jobs if j["region"] == r])
    wb.save(path)


if __name__ == "__main__":
    main()
