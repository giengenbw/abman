#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AB 与 Bestellunterlagen 自动检查工具。

用法:
  python ab_bestellunterlagen_checker.py BESTELLUNG.pdf AB.pdf -o report.json
  python .\ab_bestellunterlagen_checker.py .\BESTELLUNG.pdf .\AB.pdf -o .\AB_Check_Report

规则来源于《底盘AB检查 教程》：
1) 检查 Angebotsnummer/Kundenbestellung 是否一致；
2) 检查 Bestellunterlagen 中所有必须 Code 是否出现在 AB；
3) Bestellunterlagen 描述以 Ohne 开头的缺失 Code 可忽略；
4) AB 多出的 Code 只报告，不判错；
5) 检查净价、车型、轴距、功率、重量、交期、付款和送货地址等关键字段；
6) 生成 JSON、CSV 和易读的 HTML 报告。

依赖: pypdf（可选 OCR: ocrmypdf + tesseract，脚本会给出提示）
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError as exc:
    raise SystemExit("缺少 pypdf。请安装: pip install pypdf") from exc

CODE_RE = re.compile(r"(?<![A-Z0-9])(?:0P[A-Z0-9]{2,5}|DE[A-Z0-9]{2,5}|ZLS\d{2}|ZS[A-Z0-9]{2,5}|ZF[A-Z0-9]{2,5})(?![A-Z0-9])", re.I)
MONEY_RE = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d{3})*,\d{2})\s*EUR", re.I)

@dataclass
class CodeItem:
    code: str
    description: str
    page: int
    optional_ohne: bool = False

@dataclass
class CheckResult:
    item: str
    status: str
    bestellung: str = ""
    ab: str = ""
    note: str = ""


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def normalize_id(s: str) -> str:
    return re.sub(r"\s+", "", s or "").strip(" :")


def parse_money(value: str) -> Optional[Decimal]:
    if not value:
        return None
    try:
        return Decimal(value.replace(".", "").replace(",", "."))
    except InvalidOperation:
        return None


def extract_pdf_pages(path: Path, allow_ocr: bool = True) -> list[str]:
    def read(p: Path) -> list[str]:
        # Poppler 对 MAN 的嵌入字体和表格布局通常比 pypdf 更准确。
        if shutil.which("pdftotext"):
            result = subprocess.run(["pdftotext", "-layout", str(p), "-"], check=True, capture_output=True)
            text = result.stdout.decode("utf-8", errors="replace")
            return text.split("\f")
        reader = PdfReader(str(p))
        raw = [(page.extract_text() or "") for page in reader.pages]
        # 某些 PDF 被 pypdf 提取为逐字符换行，尽量修复。
        return [re.sub(r"(?<=\w)\n(?=\w)", "", x) for x in raw]

    pages = read(path)
    visible = sum(len(re.sub(r"\s", "", p)) for p in pages)
    if visible >= 200 or not allow_ocr:
        return pages

    if shutil.which("ocrmypdf"):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "ocr.pdf"
            subprocess.run(["ocrmypdf", "--skip-text", "--deskew", str(path), str(out)], check=True)
            return read(out)
    raise RuntimeError(
        f"{path.name} 几乎没有可提取文本。请先安装 OCRmyPDF/Tesseract，"
        "或将扫描件转换为可搜索 PDF。"
    )


def extract_codes(pages: list[str]) -> dict[str, CodeItem]:
    items: dict[str, CodeItem] = {}
    for page_no, text in enumerate(pages, 1):
        lines = [normalize_space(x) for x in text.splitlines() if normalize_space(x)]
        for i, line in enumerate(lines):
            found = list(CODE_RE.finditer(line))
            for match in found:
                code = match.group(0).upper()
                before = line[:match.start()].strip(" :-")
                after = line[match.end():].strip(" :-")
                desc = before if len(before) >= len(after) else after
                # PDF 换行时，补充相邻行作为描述，但避免页眉页脚。
                if len(desc) < 5:
                    neighbors = []
                    if i > 0:
                        neighbors.append(lines[i - 1])
                    if i + 1 < len(lines):
                        neighbors.append(lines[i + 1])
                    desc = " ".join(neighbors + [desc])
                desc = normalize_space(desc)
                optional = bool(re.search(r"\bohne\b", desc, re.I))
                if code not in items or len(desc) > len(items[code].description):
                    items[code] = CodeItem(code, desc[:500], page_no, optional)
    return items


def first_match(text: str, patterns: list[str], flags: int = re.I | re.S) -> str:
    for pat in patterns:
        m = re.search(pat, text, flags)
        if m:
            return normalize_space(m.group(1))
    return ""


def extract_fields(pages: list[str], kind: str) -> dict[str, str]:
    text = "\n".join(pages)
    fields: dict[str, str] = {}
    if kind == "bestellung":
        fields["reference"] = first_match(text, [r"Angebotsnummer\s*:\s*([^\s]+)", r"Bestellnummer\s+([^\s]+)"])
        fields["net_price"] = first_match(text, [r"Preis pro Fahrzeug\s+([\d.]+,\d{2})\s*EUR", r"Summe Preis gesamt\s+([\d.]+,\d{2})\s*EUR"])
        fields["delivery"] = first_match(text, [r"Unverbindlicher Lieferzeitraum\s+([^\n]+)"])
        fields["payment"] = first_match(text, [r"Zahlungsbedingungen\s+([^\n]+)"])
        fields["delivery_address"] = first_match(text, [r"Lieferort\s+([^\n]+)"])
    else:
        fields["reference"] = first_match(text, [r"Kundenbestellung\s+([^\s]+)"])
        fields["net_price"] = first_match(text, [r"Nettobetrag\s+([\d.]+,\d{2})\s*EUR"])
        fields["delivery"] = first_match(text, [r"Liefertermin.*?voraussichtlich\s+(?:im\s+)?([^\n]+)"])
        fields["payment"] = first_match(text, [r"Zahlungsbedingung\s*:\s*-+\s*([^\n]+)"])
        fields["delivery_address"] = first_match(text, [r"Überführung zu\s+(.{0,260}?)(?:Seite|Hinweis zur Lieferzeit)"])

    common = {
        "model": [r"Variantenbeschr(?:eibung|\.)\s+([^\n]+)"],
        "wheelbase": [r"(?:Hauptradabstand|Radstand)\s+(\d[\d.]*)\s*mm"],
        "power_kw": [r"Motorleistung(?: in KW/PS)?(?:\s*/\s*Schadstoffklasse)?\s+(?:0*)?(\d{3})\s*(?:kW|/)", r"Motorleistung\s+(\d+)\s*kW"],
        "total_weight": [r"(?m)^\s*Gesamtgewicht\s+(\d[\d.]*)\s*kg"],
        "front_axle": [r"Vorderachslast\s+(\d[\d.]*)\s*kg", r"Vorderachse\s+(\d[\d.]*)\s*kg"],
        "rear_axle": [r"Hinterachslast\s+(\d[\d.]*)\s*kg", r"Hinterachse\s+(\d[\d.]*)\s*kg"],
    }
    for key, pats in common.items():
        fields[key] = first_match(text, pats)
    return fields


def comparable_reference(value: str, ignore_version: bool) -> str:
    value = normalize_id(value).upper()
    if ignore_version:
        value = re.sub(r"_V\d+$", "", value)
    return value


def compare(best_pages: list[str], ab_pages: list[str], ignore_version: bool = False):
    best_codes = extract_codes(best_pages)
    ab_codes = extract_codes(ab_pages)
    bf = extract_fields(best_pages, "bestellung")
    af = extract_fields(ab_pages, "ab")
    checks: list[CheckResult] = []

    b_ref = comparable_reference(bf.get("reference", ""), ignore_version)
    a_ref = comparable_reference(af.get("reference", ""), ignore_version)
    checks.append(CheckResult("Angebotsnummer/Kundenbestellung", "OK" if b_ref and b_ref == a_ref else "ERROR", bf.get("reference", ""), af.get("reference", ""), "教程要求两者一致"))

    bp, ap = parse_money(bf.get("net_price", "")), parse_money(af.get("net_price", ""))
    checks.append(CheckResult("Nettopreis", "OK" if bp is not None and bp == ap else "ERROR", bf.get("net_price", ""), af.get("net_price", ""), "净价必须一致"))

    for key, title in [("model", "车型"), ("wheelbase", "轴距"), ("power_kw", "功率 kW"), ("total_weight", "总重"), ("front_axle", "前轴载荷"), ("rear_axle", "后轴载荷")]:
        b, a = normalize_space(bf.get(key, "")), normalize_space(af.get(key, ""))
        # 数值字段忽略德国千位点，例如 16.000 与 16000。
        bn = b.replace(".", "") if key in {"wheelbase", "power_kw", "total_weight", "front_axle", "rear_axle"} else b.casefold()
        an = a.replace(".", "") if key in {"wheelbase", "power_kw", "total_weight", "front_axle", "rear_axle"} else a.casefold()
        status = "OK" if b and a and bn == an else ("WARNING" if not b or not a else "ERROR")
        checks.append(CheckResult(title, status, b, a, "未提取到值时需人工核验" if status == "WARNING" else ""))

    # 交期做宽松标准化，例如 “März 2027” 与 “im März 2027”。
    norm_delivery = lambda s: re.sub(r"\b(?:im|voraussichtlich|unverbindlich(?:er)?)\b", "", normalize_space(s).lower()).strip(" .")
    bd, ad = bf.get("delivery", ""), af.get("delivery", "")
    checks.append(CheckResult("交期", "OK" if bd and ad and norm_delivery(bd) == norm_delivery(ad) else "WARNING", bd, ad, "交期语义需人工确认"))

    missing_required = [x for c, x in best_codes.items() if c not in ab_codes and not x.optional_ohne]
    missing_ohne = [x for c, x in best_codes.items() if c not in ab_codes and x.optional_ohne]
    extra = [x for c, x in ab_codes.items() if c not in best_codes]

    checks.append(CheckResult("必需 Codes", "OK" if not missing_required else "ERROR", str(len(best_codes)), str(len(ab_codes)), f"缺少 {len(missing_required)} 个必需 Code；{len(missing_ohne)} 个 Ohne Code 被规则忽略；AB 多出 {len(extra)} 个 Code（允许）"))

    # 付款条件、地址差异不能仅靠字符串判定，因此作为人工审核项展示。
    checks.append(CheckResult("付款条件", "REVIEW", bf.get("payment", ""), af.get("payment", ""), "检查是否增加了 vor Zulassung、预付款等限制"))
    checks.append(CheckResult("送货地址", "REVIEW", bf.get("delivery_address", ""), af.get("delivery_address", ""), "确认公司、街道、邮编和 Tor 信息一致"))

    return checks, missing_required, missing_ohne, extra, bf, af


def write_reports(base: Path, payload: dict) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    base.with_suffix(".json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with base.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["类型", "状态/Code", "Bestellung", "AB", "说明/描述", "页码"])
        for r in payload["checks"]:
            w.writerow(["CHECK", r["status"], r["bestellung"], r["ab"], r["item"] + ": " + r["note"], ""])
        for category in ("missing_required", "missing_ohne_ignored", "extra_in_ab"):
            for item in payload[category]:
                w.writerow([category, item["code"], "", "", item["description"], item["page"]])

    rows = "".join(
        f"<tr><td>{html.escape(r['item'])}</td><td class='{r['status']}'>{r['status']}</td><td>{html.escape(r['bestellung'])}</td><td>{html.escape(r['ab'])}</td><td>{html.escape(r['note'])}</td></tr>"
        for r in payload["checks"]
    )
    def code_list(key: str) -> str:
        data = payload[key]
        if not data:
            return "<p>无</p>"
        return "<ul>" + "".join(f"<li><b>{html.escape(x['code'])}</b> (第{x['page']}页): {html.escape(x['description'])}</li>" for x in data) + "</ul>"
    doc = f"""<!doctype html><html lang='zh'><meta charset='utf-8'><title>AB 检查报告</title>
<style>body{{font-family:Arial,'Microsoft YaHei',sans-serif;margin:28px;line-height:1.45}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #bbb;padding:7px;vertical-align:top}}th{{background:#eee}}.OK{{color:#087830;font-weight:bold}}.ERROR{{color:#b00020;font-weight:bold}}.WARNING,.REVIEW{{color:#9a6700;font-weight:bold}}code{{background:#f4f4f4}}</style>
<h1>AB 与 Bestellunterlagen 自动检查报告</h1><p>结论: <b>{html.escape(payload['overall_status'])}</b></p>
<table><tr><th>检查项</th><th>状态</th><th>Bestellung</th><th>AB</th><th>说明</th></tr>{rows}</table>
<h2>AB 缺少的必需 Codes</h2>{code_list('missing_required')}
<h2>缺失但按 Ohne 规则忽略</h2>{code_list('missing_ohne_ignored')}
<h2>AB 多出的 Codes（允许，但建议抽查）</h2>{code_list('extra_in_ab')}
<p><small>自动提取可能受扫描质量、换行和 OCR 影响。ERROR/REVIEW 项必须人工复核，SAP 价格仍需人工比对。</small></p></html>"""
    base.with_suffix(".html").write_text(doc, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="比较 MAN/Daimler AB 与 Bestellunterlagen")
    p.add_argument("bestellung", type=Path, help="Bestellunterlagen PDF")
    p.add_argument("ab", type=Path, help="Auftragsbestätigung PDF")
    p.add_argument("-o", "--output", type=Path, default=Path("AB_Check_Report"), help="报告基础文件名")
    p.add_argument("--ignore-version", action="store_true", help="比较编号时忽略末尾 _Vxxx（默认严格比较）")
    p.add_argument("--no-ocr", action="store_true", help="不尝试 OCR")
    args = p.parse_args()

    for f in (args.bestellung, args.ab):
        if not f.is_file():
            p.error(f"文件不存在: {f}")

    best_pages = extract_pdf_pages(args.bestellung, not args.no_ocr)
    ab_pages = extract_pdf_pages(args.ab, not args.no_ocr)
    checks, missing, ignored, extra, bf, af = compare(best_pages, ab_pages, args.ignore_version)
    overall = "不正确/需供应商澄清" if any(x.status == "ERROR" for x in checks) else ("需人工复核" if any(x.status in {"WARNING", "REVIEW"} for x in checks) else "正确")
    payload = {
        "overall_status": overall,
        "bestellung_file": str(args.bestellung),
        "ab_file": str(args.ab),
        "bestellung_fields": bf,
        "ab_fields": af,
        "checks": [asdict(x) for x in checks],
        "missing_required": [asdict(x) for x in missing],
        "missing_ohne_ignored": [asdict(x) for x in ignored],
        "extra_in_ab": [asdict(x) for x in extra],
        "limitations": ["SAP 订单价格无法从本地 PDF 自动取得，需人工核对", "扫描 PDF 的 OCR 可能误识别 Code", "付款条款和地址为语义审核项"],
    }
    write_reports(args.output, payload)
    print(json.dumps({"overall_status": overall, "output": str(args.output), "errors": [asdict(x) for x in checks if x.status == "ERROR"], "missing_required_count": len(missing), "extra_in_ab_count": len(extra)}, ensure_ascii=False, indent=2))
    return 2 if any(x.status == "ERROR" for x in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
