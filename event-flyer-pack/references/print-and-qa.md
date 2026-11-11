# 尺寸、组装与验收

## 先明确生产边界

- A6 裁切尺寸：105×148 mm，300 DPI 约 1240×1748 px；不是 2:3。
- 完整 pack：A6 front/back PNG；A4 four-up front/back PDF；桌卡 PNG/PDF；Story JPEG。不得因只做过单张就宣称整套物料验收通过。
- 数字单张只保证用户要求且实际导出的尺寸，不擅自改成 A6。
- 上采样不会凭空增加细节；必须标记原始分辨率、实际尺寸与放大情况。
- 默认产物无出血、无 CMYK/印刷 ICC/PDF-X 认证、无刀模与粘接襟翼；不得称为印厂已确认的 bleed master。真正商业印刷须先询问印厂规格，按实际出血生成/延展画面并另行验收，不把简单加白边算出血。
- A4 上 4 张原尺寸 A6 几乎占满纸面，外侧不能再无损添加裁切标记。本适配默认四拼为 **95% A6 = 99.75×140.6 mm**，留外侧裁切标记，明确不是足尺寸 A6。打印选 Actual size / 100%；不叠加“适合纸张”缩放。若要求足尺寸 A6，改用更大纸张或先确认不要裁切标记。
- 桌卡为 105×296 mm 展开，148 mm 处折叠；每个半面 105×148 mm。顶面旋转 180°，不是水平镜像。不承诺所有纸材都能自行站稳，正式印量前先打样。

## 运行约定

`PY` 为安装了 scripts/requirements.txt 的 Python，`SKILL_DIR` 为技能目录绝对路径，`OUT` 为当前任务输出目录，`EVENT_URL` 为用户确认的最终 URL。运行前建立输出目录。模板和资源只读，所有生成写到任务目录。

### 在叠码前处理底图比例

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" normalize "$OUT/front-generated.png" \
  "$OUT/front-base.png" --width 1240 --height 1748 --matte '#181818'

"$PY" "$SKILL_DIR/scripts/formats.py" normalize "$OUT/story-generated.png" \
  "$OUT/story-base.png" --width 1080 --height 1920 --matte '#181818'
```

不裁剪、不拉伸；不足目标比例时扩画布。用图片读取工具检查边缘和占位位置，必要时回到设计修改；不要为凑尺寸接受明显黑边。输出 `qr_verified: false` 是正常的——此阶段是底图，接着叠真实 QR。

### 手动叠码

```bash
"$PY" "$SKILL_DIR/scripts/overlay_qr.py" "$OUT/front-base.png" "$OUT/qr.png" \
  "$OUT/front.png" --x "$X" --y "$Y" --size "$SIDE" --verify "$EVENT_URL"
```

坐标是导出底图的像素，QR 必须完全在画布内。不在最后叠码后再静默缩图。脚本会白底清除整个占位区，并检查保存后的原像素 QR 选区；错误 URL、越界、多个候选白区均需显式处理。

### 四拼

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" four-up "$OUT/front.png" "$OUT/back.png" \
  --out "$OUT" --slug "$SLUG" --verify "$EVENT_URL" > "$OUT/four-up-qa.json"
```

从最终 PDF 以 300 DPI 渲染四个格子，逐格解码；两面共 8 次。双面打印正反对齐取决于打印机，先打样，不保证走纸误差。

### 桌卡

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" tent "$OUT/tent-top.png" \
  "$OUT/tent-bottom.png" "$OUT/tent-card.png" --verify "$EVENT_URL" \
  > "$OUT/tent-qa.json"
```

两个半面事先都是 A6、正向并已叠码。脚本导出 PNG/PDF，然后分别裁取两半、把顶面转正验码，共 4 次；不要试图用单码检测器一次解整个双码画布。

### Story 最后转 JPEG

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" story "$OUT/story.png" \
  "$OUT/instagram-story.jpg" --verify "$EVENT_URL" > "$OUT/story-qa.json"
```

源图须是 1080×1920。脚本在最终 JPEG 上重新解码，不能只检查 PNG 原稿。发布平台可能再次压缩；本地通过不代表平台转码后也通过。重要内容离上下端各约 250 px，QR 不贴底。

## 验收记录

在任务目录保存 qa.json，记录：

```json
{
  "scope": "single-front-or-full-pack",
  "fictional_demo": false,
  "generation_job_ids": [],
  "copy_check": {"status": "pass-or-unverified", "checked_fields": []},
  "assets": [
    {"file": "front.png", "pixels": [1240, 1748], "expected_url": "user-confirmed-url", "decoded_url": "actual-result", "qr_pass": true}
  ],
  "print": {"bleed_mm": 0, "cmyk_verified": false, "printer_proofed": false},
  "limitations": []
}
```

至少检查：
1. 标题、日期/星期、时段/时区、场地、票价/入场、CTA 与用户确认文案一致；不漏字、不多字、不乱码。
2. QR 不压字、不被裁切、四模块以上静区、目的 URL 逐字一致。
3. 在实际交付的图像和 PDF 上检查，不拿底稿成功代替最终成功。
4. 检查真实尺寸、纸张尺寸与 PDF 页数；A4 四拼实际 tile 尺寸如实告知。
5. 若声称目的网页可访问，必须确实访问并确认；脚本只做 URL 语法和编码，不检查线上网站。需要网页检查时遵循当前公共数据/浏览器规则，不请求秘密。
6. 自动解码不等于真实手机、暗光、远距离和印刷打样测试；未做的写“未测试”。
7. 只交付选中的、通过检查的最终文件，保留对应生成回执。

## 不付费的工具自测

```bash
"$PY" -m unittest discover -s "$SKILL_DIR/tests" -v
```

测试创建合成底图和 QR，检查单码覆盖、无效 URL、错误目的地、白区歧义/越界、PDF 四拼逐格、桌卡旋转、JPEG 二次导出。它验证本地工具链，不替代真实活动的排版目检或商业印刷打样。
