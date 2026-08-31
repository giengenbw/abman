#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AB 与 Bestellunterlagen 自动检查工具 V4。

用法:
  python ab_bestellunterlagen_checker_v4.py BESTELLUNG.pdf AB.pdf -o report

说明:
- 本文件与 ab_bestellunterlagen_checker_v3.py 放在同一目录。
- V3 的所有检查、提取、OCR 和报告格式保持不变。
- V4 新增：所有技术码在 JSON、CSV、中文 HTML、德文 HTML 中均逐一生成检查项。

技术码逐项状态:
- OK: Bestellunterlagen 中的 Code 在 AB 中存在；
- ERROR: Bestellunterlagen 中的必需 Code 在 AB 中缺失；
- IGNORED: 描述以/含 Ohne 的 Code 在 AB 中缺失，按规则忽略；
- INFO: Code 仅在 AB 中出现，允许但建议抽查。
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

try:
    import ab_bestellunterlagen_checker_v3 as v3
except ImportError as exc:
    raise SystemExit(
        "无法导入 ab_bestellunterlagen_checker_v3.py。"
        "请将 V3 与 V4 脚本放在同一目录。"
    ) from exc


CODE_STATUS_NOTES = {
    "OK": "Der Code ist sowohl in den Bestellunterlagen als auch in der AB vorhanden.",
    "ERROR": "Der erforderliche Code aus den Bestellunterlagen ist in der AB nicht vorhanden.",
    "IGNORED": "Der „Ohne“-Code aus den Bestellunterlagen ist in der AB nicht vorhanden und wird gemäß der Regel ignoriert.",
    "INFO": "Der Code ist nur in der AB vorhanden. Dies ist zulässig, eine stichprobenartige Prüfung wird jedoch empfohlen.",
}


def make_code_checks(
    best_pages: list[str], ab_pages: list[str]
) -> list[v3.CheckResult]:
    """为技术码并集生成一一对应、每个 Code 恰好一条的检查记录。"""
    best_codes = v3.extract_codes(best_pages)
    ab_codes = v3.extract_codes(ab_pages)
    rows: list[v3.CheckResult] = []

    # 先按 Bestellunterlagen 的出现顺序检查，随后追加仅存在于 AB 的 Code。
    for code, best_item in best_codes.items():
        ab_item = ab_codes.get(code)
        if ab_item is not None:
            status = "OK"
            ab_value = f"Seite {ab_item.page}: {ab_item.description}"
        elif best_item.optional_ohne:
            status = "IGNORED"
            ab_value = ""
        else:
            status = "ERROR"
            ab_value = ""

        rows.append(
            v3.CheckResult(
                item=f"Code {code}",
                status=status,
                bestellung=f"Seite {best_item.page}: {best_item.description}",
                ab=ab_value,
                note=CODE_STATUS_NOTES[status],
            )
        )

    for code, ab_item in ab_codes.items():
        if code in best_codes:
            continue
        rows.append(
            v3.CheckResult(
                item=f"Code {code}",
                status="INFO",
                bestellung="",
                ab=f"Seite {ab_item.page}: {ab_item.description}",
                note=CODE_STATUS_NOTES["INFO"],
            )
        )

    # 二次一致性检查：并集中的每个 Code 必须且只能出现一次。
    expected = set(best_codes) | set(ab_codes)
    actual = [row.item.removeprefix("Code ") for row in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise RuntimeError("技术码逐项检查生成失败：存在重复或遗漏的 Code。")
    return rows


def compare(
    best_pages: list[str],
    ab_pages: list[str],
    ignore_version: bool = False,
):
    """运行 V3 比较，并在汇总 Code 行后插入所有技术码的逐项检查。"""
    checks, missing, ignored, extra, bf, af = v3.compare(
        best_pages, ab_pages, ignore_version
    )
    code_checks = make_code_checks(best_pages, ab_pages)

    insert_at = next(
        (i + 1 for i, row in enumerate(checks) if row.item == "必需 Codes"),
        len(checks),
    )
    checks[insert_at:insert_at] = code_checks
    return checks, missing, ignored, extra, bf, af


def main() -> int:
    p = argparse.ArgumentParser(
        description="比较 MAN/Daimler AB 与 Bestellunterlagen（V4：技术码逐项检查）"
    )
    p.add_argument("bestellung", type=Path, help="Bestellunterlagen PDF")
    p.add_argument("ab", type=Path, help="Auftragsbestätigung PDF")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("AB_Check_Report"),
        help="报告基础文件名",
    )
    p.add_argument(
        "--ignore-version",
        action="store_true",
        help="比较编号时忽略末尾 _Vxxx（默认严格比较）",
    )
    p.add_argument("--no-ocr", action="store_true", help="不尝试 OCR")
    args = p.parse_args()

    for file_path in (args.bestellung, args.ab):
        if not file_path.is_file():
            p.error(f"文件不存在: {file_path}")

    best_pages = v3.extract_pdf_pages(args.bestellung, not args.no_ocr)
    ab_pages = v3.extract_pdf_pages(args.ab, not args.no_ocr)
    checks, missing, ignored, extra, bf, af = compare(
        best_pages, ab_pages, args.ignore_version
    )

    overall = (
        "不正确/需供应商澄清"
        if any(item.status == "ERROR" for item in checks)
        else (
            "需人工复核"
            if any(item.status in {"WARNING", "REVIEW"} for item in checks)
            else "正确"
        )
    )

    payload = {
        "overall_status": overall,
        "bestellung_file": str(args.bestellung),
        "ab_file": str(args.ab),
        "bestellung_fields": bf,
        "ab_fields": af,
        "checks": [asdict(item) for item in checks],
        "missing_required": [asdict(item) for item in missing],
        "missing_ohne_ignored": [asdict(item) for item in ignored],
        "extra_in_ab": [asdict(item) for item in extra],
        "limitations": [
            "SAP 订单价格无法从本地 PDF 自动取得，需人工核对",
            "扫描 PDF 的 OCR 可能误识别 Code",
            "付款条款和地址为语义审核项",
        ],
    }
    v3.write_reports(args.output, payload)

    code_checks = [item for item in checks if item.item.startswith("Code ")]
    print(
        json.dumps(
            {
                "overall_status": overall,
                "output": str(args.output),
                "html_zh": str(args.output) + "_ZH.html",
                "html_de": str(args.output) + "_DE.html",
                "errors": [
                    asdict(item) for item in checks if item.status == "ERROR"
                ],
                "technical_code_check_count": len(code_checks),
                "missing_required_count": len(missing),
                "extra_in_ab_count": len(extra),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 2 if any(item.status == "ERROR" for item in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
