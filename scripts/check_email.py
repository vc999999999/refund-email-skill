#!/usr/bin/env python3
"""退款邮件发出前的机械检查。

用法:
    python3 check_email.py <邮件文件> <first-contact|follow-up|final-notice>

文件内容: 第一行主题 + 空行 + 英文正文(不含中文对照)。主观项
(语气/语法/事实对应/中文对照一致性)不归本脚本管,由模型按 SKILL.md 第 4 步自查。
退出码: 0 = 全部通过; 1 = 有失败项,改完重跑。
"""
import re
import sys

EARLY_STAGES = {"first-contact", "follow-up"}

# 所有阶段都禁止——诉讼/曝光超出退款邮件应有的克制
FORBIDDEN_ALWAYS = [
    (r"\bsue\b|\bsued\b|\bsuing\b", "sue/sued/suing"),
    (r"\blawyer\b|\battorney\b", "lawyer/attorney"),
    (r"legal\s+(?:action|proceeding|step|recourse)", "legal action/proceedings"),
    (r"\bexpose\s+(?:you|this|your)\b", "expose (targeted)"),
    (r"go\s+public\b", "go public"),
    (r"social\s+media", "social media"),
]
# 仅首封/跟进禁止——这两张牌只能打在 final-notice
FORBIDDEN_EARLY = [
    (r"charge[\s-]?back", "chargeback"),
    (r"\bdispute\b", "dispute"),
    (r"consumer\s+protection", "consumer protection"),
]

AMOUNT = re.compile(
    r"(?:[$€£¥]\s?\d[\d,.]*"               # 符号前置: $29.99, €1,200
    r"|\b(?:USD|EUR|GBP|CNY)\s+\d[\d,.]*"  # 码前置: USD 29.99
    r"|\d[\d,.]+\s?(?:USD|EUR|GBP|CNY|dollars?\b))",  # 码后置: 29.99 USD
    re.I,
)
ORDER_ID = re.compile(r"#\s?[A-Za-z0-9][A-Za-z0-9-]{4,}")
DATE = re.compile(
    r"(?:"
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?(?:\s+\d{4})?"  # Oct 3, 2024 或 Oct 3
    r"|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}"  # 3 October 2024
    r"|\b\d{4}-\d{2}-\d{2}\b"                     # 2024-10-03
    r"|\b\d{1,2}/\d{1,2}/(?:\d{2}|\d{4})\b"       # 10/3/2024
    r")"
)
PLACEHOLDER = re.compile(r"\{[^}]*\}|【[^】]*】|\bTODO\b|\bFIXME\b|_{3,}|X{3,}", re.I)
GREETING = re.compile(r"^\s*(?:Dear|Hello|Hi)\b", re.M)
SIGNOFF = re.compile(r"(Best\s+regards|Regards|Sincerely|Kind\s+regards)", re.I)


def main():
    valid_stages = set(EARLY_STAGES) | {"final-notice"}
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <邮件文件> <first-contact|follow-up|final-notice>")
        return 1
    if sys.argv[2] not in valid_stages:
        print(f"✗ 阶段参数无效: {sys.argv[2]!r}，合法值: {sorted(valid_stages)}")
        return 1
    path, stage = sys.argv[1], sys.argv[2]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"✗ 无法读取文件: {e}")
        return 1

    raw_lines = text.splitlines()
    if not raw_lines or not raw_lines[0].strip():
        print("✗ 文件格式错误：第一行必须是主题")
        return 1
    subject = raw_lines[0].strip()
    body = "\n".join(raw_lines[1:]).strip()
    if not body:
        print("✗ 正文为空")
        return 1
    if re.search(r"[\u4e00-\u9fff]{10,}", body):
        print("⚠ 正文疑似包含中文，请确认临时文件仅含英文正文")

    results = []

    if stage == "first-contact":
        results.append(("Refund Request" in subject, "主题含 Refund Request"))
    else:
        ok = ("Re:" in subject) or ("Refund Request" in subject)
        results.append((ok, "主题是原邮件串的回复(Re:)或 Refund Request"))

    m = PLACEHOLDER.search(text)
    detail = "" if m is None else f"(发现: {m.group(0)!r})"
    results.append((m is None, f"无占位符残留{detail}"))
    results.append((ORDER_ID.search(body) is not None, "正文含订单号(#…)"))
    results.append((AMOUNT.search(body) is not None, "正文含金额"))
    results.append((DATE.search(body) is not None, "正文含购买/扣款日期"))
    results.append((re.search(r"refund", body, re.I) is not None, "正文含明确诉求(refund)"))
    results.append((GREETING.search(body) is not None, "有称呼(Dear / Hello / Hi …)"))
    results.append((SIGNOFF.search(body) is not None, "有落款(Best regards…)"))

    banned = list(FORBIDDEN_ALWAYS) + (FORBIDDEN_EARLY if stage in EARLY_STAGES else [])
    hits = [label for pattern, label in banned if re.search(pattern, text, re.I)]
    results.append((not hits, "无违禁词" if not hits else f"含违禁词: {'、'.join(hits)}"))

    wc = len(body.split())
    results.append((wc <= 250, f"正文长度 {wc} 词(≤250)"))

    fails = 0
    for ok, label in results:
        print(("✓ " if ok else "✗ ") + label)
        fails += 0 if ok else 1
    if fails:
        print(f"—— {fails} 项未过，改完重跑。")
        return 1
    print("—— 全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
