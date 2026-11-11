# 生成活动底图

使用当前可用图像工具，按 `templates/prompts.md` 生成包含画面、排版和空白 QR 区的完整设计。每次只生成一个物料，不让工具绘制可用二维码。

调用前读取 `okou generate image -h`，按当前帮助选择可用尺寸；本 pack 的提示词已包含完整视觉要求，使用 raw-prompt，不额外套无关插画样式。将 `<supported-size>` 替换为当前工具支持且接近目标比例的尺寸。

```bash
okou generate image \
  --raw-prompt "$(< "$OUT/front-prompt.txt")" \
  --size "<supported-size>" --quality high --format png \
  --wait --visibility only-me --json > "$OUT/front-generation.json"
```

- 等待完成并使用返回图像；保存原始提示词、job ID、实际返回宽高。
- 超时后查询同一 generation ID：`okou generate get <generation-id> --refresh --json`，不要重新提交来检查进度。
- 完成后下载实际成图：`okou generate get <generation-id> --out "$OUT/front-generated.png"`。
- 返回尺寸与目标不符时，先用 `formats.py normalize` 等比装入目标画布，再叠真实 QR；不拉伸、不静默裁切文字，检查扩展边缘。
- 先读取本地参考图；若需要传参考，仅使用当前接口支持且用户已授权的方式，不擅自公开图片。读取参考并描述视觉通常足够。
- 出图失败保留回执并按当前工具诊断；不无限重试、不重复付费试跑。

四拼、旋转拼接与最终验码由本地脚本完成，不再调用图像服务。
