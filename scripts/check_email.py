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
    (r"\bsue\b", "sue"), (r"\bsuing\b", "suing"),
    (r"\blawyer\b", "lawyer"), (r"\battorney\b", "attorney"),
    (r"legal\s+action", "legal action"),
    (r"social\s+media", "social media"), (r"\bexpose\b", "expose"),
]
# 仅首封/跟进禁止——这两张牌只能打在 final-notice
FORBIDDEN_EARLY = [
    (r"charge[\s-]?back", "chargeback"),
    (r"\bdispute\b", "dispute"),
    (r"consumer\s+protection", "consumer protection"),
]

AMOUNT = re.compile(
    r"(?:[$€£¥]\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?(?:USD|EUR|GBP|CNY|dollars?\b))",
    re.I,
)
ORDER_ID = re.compile(r"#\s?[A-Za-z0-9][A-Za-z0-9-]{2,}")
DATE = re.compile(
    r"(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}"
    r"|\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b)"
)
PLACEHOLDER = re.compile(r"\{[^}]*\}|【[^】]*】|\bTODO\b|\bFIXME\b|_{3,}|X{3,}", re.I)
GREETING = re.compile(r"^\s*Dear\b", re.M)
SIGNOFF = re.compile(r"(Best\s+regards|Regards|Sincerely|Kind\s+regards)", re.I)


def main():
    valid_stages = set(EARLY_STAGES) | {"final-notice"}
    if len(sys.argv) != 3 or sys.argv[2] not in valid_stages:
        print(__doc__)
        return 1
    path, stage = sys.argv[1], sys.argv[2]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"✗ 无法读取文件: {e}")
        return 1

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        print("✗ 文件为空")
        return 1
    subject, body = lines[0], "\n".join(lines[1:])

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
    results.append((GREETING.search(body) is not None, "有称呼(Dear …)"))
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
