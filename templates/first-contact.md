# 首封退款邮件模板

**Subject:** `Refund Request – Order #XXXXX – 产品名`

```
Dear Customer Support,        ← 对方署名有名字就用 Dear {Name},

I am writing to request a refund for {产品/订阅名} (Order #{订单号},
purchased on {日期} for {金额+币种}).

{第 2 段：原因，按场景从下面选一个骨架，事实必须来自用户}

I am requesting a full refund of {金额} to my original payment method.
[B 场景加一句:] Please also cancel my subscription to prevent
future charges.

I have attached {附件列表：receipt / screenshot of ...} for your
reference. Please let me know if you need any additional information.

Thank you for your time.
Best regards,
{姓名}
(账户邮箱: {email})
```

## 第 2 段各场景骨架（来自 scenarios.md，选一）

- **A 误购/重复：** "I was charged twice for the same purchase by mistake."
- **B 自动续费：** "This was the first automatic renewal after a free trial, which I forgot to cancel. I have not used the service since the charge, and I am contacting you as soon as I noticed it."
- **C 服务缺陷：** "The product does not match its description: {1–3 条具体、可验证的问题，各带日期}"
- **D 未交付：** "I have not received the product/service despite payment on {日期}, which is now {N} days ago."
- **E 取消仍被扣：** "I cancelled my subscription on {日期}, before the trial period ended, yet I was charged {金额} on {日期}."
- **F 未授权：** "I did not authorize this charge."
- **G 未使用/改变主意：** "I purchased {产品} on {日期} but have not used it, and I am requesting a refund within your stated refund window."

## 规则

- 所有 `{}` 内容必须来自用户提供的信息；给不出的**整句删除**，不留占位符。
- 全文首封推荐 ≤180 词（短比长好）；脚本硬限 250 词。
- 首封绝不出现 chargeback / legal / dispute 字眼。
