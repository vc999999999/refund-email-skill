# refund-email — 海外退款邮件技能

帮中国用户向海外商家/服务申请退款的 AI 技能（Agent Skill）。用户用中文描述情况，技能负责把流程走对、把英文退款信写好。

## 为什么需要它

模型本身就会写英文退款信——这个技能的价值不在"教它写信"，而在五件裸模型做不到稳定的事：

1. **把要素问齐**——缺订单号/日期/金额的信，客服大概率直接不回。要素不齐不起草。
2. **把渠道找对**——Apple、Steam、Google Play 的退款根本不走客服邮箱。内置人工核实的平台渠道速查，库外商家强制 web search 核实，绝不编造 support@xxx。
3. **把策略选对**——七个场景（误购、自动续费、服务缺陷、未交付、取消仍被扣、未授权扣款、未使用）各自的论证要点和雷区，以及"首封克制 → 3-5 个工作日跟进 → 最后通知才亮 chargeback → 银行拒付"的完整升级链路。
4. **把事实守住**——只用用户提供的事实，禁止为了让信更有力而编造故障或承诺。
5. **把检查做实**——附确定性检查脚本 `scripts/check_email.py`：主题格式、订单号/日期/金额齐全、占位符残留、按阶段禁词（首封/跟进禁 chargeback、dispute）、长度、称呼落款。机械项脚本说了算，不靠模型自查。

## 工作流

```
第 0 步 渠道检查（不走邮件的平台直接给正确入口，不写信）
  ↓
第 1 步 信息收集（一条中文消息问齐 9 项要素）
  ↓
第 2 步 场景判定（A–G，取论证要点和雷区）
  ↓
第 3 步 起草（英文正文 + 逐段中文对照 + 附件建议）
  ↓
第 4 步 发出前检查（脚本机械项 + 模型主观项）
  ↓
跟进链路（跟进信 → 最后通知 → 银行拒付指引）
```

## 安装

技能目录就是仓库根目录，克隆到你的技能目录即可：

```bash
# ZCode
git clone https://github.com/vc999999999/refund-email-skill ~/.agents/skills/refund-email

# Claude Code（同格式，直接兼容）
git clone https://github.com/vc999999999/refund-email-skill ~/.claude/skills/refund-email
```

装好后在对话里提到"退款、被扣费、自动续费想退"等就会自动触发，也可以显式 `/refund-email`。

## 目录结构

```
refund-email/
├── SKILL.md                      # 主工作流
├── references/
│   ├── vendor-channels.md        # 平台退款渠道事实库（标注核实日期）
│   └── scenarios.md              # A–G 场景 → 论证要点 / 雷区 / 成功率预期
├── templates/
│   ├── first-contact.md          # 首封邮件骨架（含各场景原因段）
│   ├── follow-up.md              # 跟进信（3–5 个工作日无回复）
│   └── final-notice.md           # 最后通知（唯一允许提 chargeback 的位置）
└── scripts/
    └── check_email.py            # 发出前机械检查（无需第三方依赖）
```

## 维护

- `references/vendor-channels.md` 中的平台政策会变，条目均标注人工核实日期，建议每半年复核一次。
- 遇到库外商家时技能会现场 web search 核实；核实过的商家欢迎提 PR 沉淀进事实库（附来源和日期）。
- 检查脚本只用 Python 标准库，`python3 scripts/check_email.py <邮件文件> <first-contact|follow-up|final-notice>`。

## 边界

- 不处理国内电商退款（淘宝/京东等走平台售后，不用写信）。
- 不保证退款成功——技能提高的是表达、要素与流程质量，结果是商家决定的。

## License

MIT
