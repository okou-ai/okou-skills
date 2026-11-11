---
name: event-flyer-pack
description: "制作具体活动的宣传单与真实可扫码二维码；适用于活动 flyer、宣传物料包、A6 正反面、A4 四拼、桌卡与 Story。支持仅做一张或完整套装，使用当前可用图像工具出图，再叠加真实二维码并逐件验码。"
---

# Event Flyer Pack

将活动信息变成统一风格的宣传物料。让图像工具负责画面与排版；用本地脚本生成、叠加、验证真实二维码，不让图像工具绘制可用二维码。

## 范围与准备

- 使用当前可用图像工具出图；调用步骤见 `references/image-generation.md`。
- 默认使用大号高对比衬线标题、暗色氛围光影、钴蓝/奶油白/炭黑。读取 `references/style.md` 与随附参考图；只参考视觉，不复制虚构活动信息。用户本次风格或品牌要求优先。
- 单张请求只做单张；完整 pack 制作 A6 正反面、A4 四拼正反 PDF、折叠桌卡、1080×1920 Story。范围不清时只问“单张还是整套”。每个独立设计先出一版，仅在验收失败或用户需要备选时追加。
- 仅手动调用，不创建自动任务，不自动发帖、群发、公开发布、下印刷订单或创建短链。文件默认私有；涉及第三方账户或费用遵循当前授权与平台规则。

将 `SKILL_DIR` 设置为本技能目录的绝对路径，`OUT` 设置为本次任务目录。技能资源只读，所有输出写入任务目录。参考图以无损 base64 封装，先还原并校验，再用图片读取工具查看：

```bash
mkdir -p "$OUT"
python3 "$SKILL_DIR/scripts/restore_reference.py" "$OUT/style-reference.png"
```

校验失败时停止使用该参考，不默默跳过。准备步骤不调用图像服务。

## 1. 确认活动信息

按 `templates/event-spec.json` 的结构记录本次输入，不修改技能内模板。确认标题、日期、起止时间与时区、场地/线上入口、入场方式、CTA、二维码 URL、语言、物料范围与尺寸。可选项包括副标题、议程、亮点、主办方和已授权图片/Logo。

只追问缺失的关键信息，不沿用演示日期/地址/URL，不假设免费。概念稿可标 TBA；没有真实 URL 就不生成假二维码，也不称为可发布终稿。虚构演示须明显标记。日期与星期冲突时先确认。

URL 默认 HTTPS，必须与用户确认值完全一致，不擅加 UTM、删参数或换成第三方短链。长 URL 可建议自有短链接或扩大二维码。拒绝钓鱼/恶意用途，不把密钥、会话或一次性登录令牌编码进宣传二维码。

## 2. 生成完整底图

读取 `templates/prompts.md` 中所需物料的模板，填入确切文案、场景、配色和占位坐标，删除未提供的可选字段。采用“完整设计 + 空白 QR 区”，不要让占位花括号进入成图。

每个独立设计单独出图：front、back、两个桌卡半面、Story。四拼与桌卡旋转由本地脚本完成，不额外出图。

强制要求固定位置、边长的纯白方形 QR 空位，内部无图案、文字、阴影或圆角，不与文案冲突。即使底图画了假 QR，也必须完全清白覆盖后换成真实码。

等待生成完成，保存 job ID、提示词、原件和实际返回尺寸；不要重复提交来查询进度。印刷前按 `references/print-and-qa.md` 处理尺寸，再叠 QR。A6 为 105×148 mm，约 1240×1748 px @300 DPI，不是 2:3；不拉伸或静默裁字，扩画布须目检，上采样不等于新增细节。

## 3. 生成并叠加真实二维码

在任务专用虚拟环境安装 `scripts/requirements.txt`。沿用 `SKILL_DIR`、`OUT`，将 `EVENT_URL` 设置为用户确认的最终 URL。

```bash
python3 -m venv ./generated/flyer-env
./generated/flyer-env/bin/python -m pip install -r "$SKILL_DIR/scripts/requirements.txt"
PY=./generated/flyer-env/bin/python

"$PY" "$SKILL_DIR/scripts/generate_qr.py" --url "$EVENT_URL" \
  --error H --border 4 --box-size 16 --png "$OUT/qr.png" --svg "$OUT/qr.svg"

"$PY" "$SKILL_DIR/scripts/overlay_qr.py" "$OUT/front-base.png" \
  "$OUT/qr.png" "$OUT/front.png" --auto-detect --verify "$EVENT_URL"
```

自动检测不唯一、未识别或位置不对时，检查图片，再用 `--x X --y Y --size S`；不要盲选最大白块，不同时传手动坐标与 `--auto-detect`。

脚本检查边界，清空整张白底卡，按整数像素模块重绘真实码并保留四模块静区，再从最终导出的原像素选区解码。URL 不完全一致即失败，不交付该文件。复用同一 QR 到其他物料并逐件验码；默认使用普通黑白码，不加 Logo 或渐变。

## 4. 按需组装物料

按 `references/print-and-qa.md` 使用 `scripts/formats.py`：

- `normalize`：将底图等比装入目标画布，在此之后再叠 QR。
- `four-up`：生成 A4 四拼正反 PDF，默认 95% A6，给裁切标记留空间，并告知实际尺寸。
- `tent`：将两张已验码 A6 半面旋转拼接，输出 PNG/PDF；顶面旋转 180°，不是左右镜像文字。
- `story`：从已验码的 1080×1920 PNG 导出 JPEG，并在 JPEG 上再验码。

多码输出逐格/逐半面解码，PDF 渲染最终页面后验码。不要把整张多码页未识别误判为每个码都坏了，也不要把单张底稿成功当作整套验收成功。

## 5. 验收与交付

按 `references/print-and-qa.md` 目检最终文件：逐字核对标题、日期/星期、时间/时区、场地、入场、CTA、URL；检查层级、缺漏/乱码、截断和 QR 重叠。自动解码只证明编码，不证明活动真实、网页可用、手机扫描或印刷效果；只报告实际做过的检查。

在任务目录保存 `qa.json`：文案检查状态、实际尺寸、job ID、每件物料的预期/解码 URL、PDF 页数与印刷限制。验码失败或关键信息未核对的文件不得标为正式终稿。

Web 交付前读取 `okou web upload-file -h`，上传每个要展示的最终图片；整套可另打包私有 ZIP。不要只给本地路径，不上传未选草图、密钥或缓存，不自动发到外部平台。

简要回复文件链接、实际制作范围、逐件验码结果与必要印刷限制。只做了单张就明确说单张，不称为整套印刷物料已测试。

## 资源

- `templates/prompts.md`、`templates/event-spec.json`：提示词与空白活动输入结构。
- `references/image-generation.md`、`references/style.md`、`references/print-and-qa.md`：出图、视觉、组装与验收。
- `assets/style-reference.png.b64`、`scripts/restore_reference.py`：参考图与校验还原工具。
- `scripts/generate_qr.py`、`scripts/overlay_qr.py`：真实二维码生成、叠加与验码。
- `scripts/formats.py`、`tests/test_tools.py`：物料组装与不调用图像服务的工具测试。
- `NOTICE.md`、`LICENSE.upstream.md`：来源和上游 MIT 声明，分发时一同保留。
