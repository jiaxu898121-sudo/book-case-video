# 输入、过程与输出契约

## 人类输入：最小指令

> 用 $book-case-video 做第006期《书名》（作者），围绕“一个关系问题”讲解。资料为上传文件或网址。沿用系列语言、A版封面、配乐和保存路径，完成MP4，并检查对话是否口语化。

可选覆盖：资料范围、受众、时长、语言、声音、配乐、封面停留时间、仅脚本/仅预览/成片。未覆盖时沿用已确认profile。

## 机器输入：episode.json

JSON Schema：episode.schema.json；示例：../examples/intimate-relationships.json。

顶层：
- episode：正整数，展示时补足三位。
- slug：小写英文、数字与连字符，不能包含路径。
- book：title、author、coverage（selected_topics/whole_book）。
- sources：id、kind、locator、read_scope、verification。
- claims：id、text、type、source_ids、conditions、limits。
- output：delivery_dir（可为空；空时build只生成工程，render须给--delivery）、basename遵循期数与slug，不在脚本中硬编码另一位用户的路径。
- style：series_name、cover_seconds、fps、width、height、accent、background、cream。
- cover：lead_lines（两行）、keyword、tag_zh、tag_en、subtitle_lines（两行）。
- music：path（相对episode.json，或显式绝对路径，可为空）、provenance、volume。没有音乐时如实记录，不静默捏造。
- reviews：source/oral/translation，各含status（pending/passed）、notes。passed代表实际人工/模型编辑已检查，不由格式脚本自动设置。
- scenes：每场id、ey_zh、ey_en、title_lines、layout、nodes、claim_ids、case_kind、case_source_id、summary、lines。
- lines：id、speaker（narrator/A/B）、zh、en、voice、duration_sec（测量后填）。audio文件由脚本按场景与台词ID确定性命名。

case_kind是original时source_id可为空，但与理论相关的claim_ids仍要有来源；book/research案例必须给case_source_id。声音是预设合成声线，不表示真实人物。

## 过程产物

每期独立目录：
```
episode.json                  # 经编辑的单一事实源
voice/scene-line.mp3           # 独立语音
cover-3x4.png / cover-9x16.png
project/src/episode-data.json  # 确定性生成，勿手工作为新事实源
project/src/BookVideo.tsx
project/public/...
review.md                     # 内容与口语检查记录
```

reviews为passed后，validate检查格式与结构；measure用真实音频时长更新duration_sec；build生成配音片段时序、英文字幕时序、工程与SRT。后续改稿更新episode.json，然后重做有变动的语音、measure与build。旧音频复用必须比对脚本与voice的缓存指纹，不能仅检查文件存在。

## 最终输出

```
固定交付目录/NNN-slug-with-cover.mp4
当期工作目录/NNN-slug.en.srt
当期工作目录/cover-3x4.png
当期工作目录/cover-9x16.png
当期工作目录/episode.json
当期工作目录/review.md
当期工作目录/qa.json
```

qa.json记录实际检查：文件、尺寸、时长、音轨、完整解码是否成功、抽帧路径；视觉/听审状态初始pending，编辑实际检查后再更新。不是自动生成“全通过”证书。

## 验收不变量

1. 单一episode驱动封面编号、标题、视频名和时序。
2. 各配音不重叠，时长为正且有限；封面偏移只加入一次。
3. 英文字幕仅覆盖其语音片段，不跨入下一角色。
4. source/claim引用均存在；部分资料不能声称整书覆盖。
5. 图解必须来自本期内容，不能残留上一书的框架与标签。
6. 最新交付文件已验证；旧版归档后再替换，不丢弃唯一可用版本。
