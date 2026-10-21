# 书籍蒸馏与案例视频 · 复用说明

技能名：`book-case-video`。完整技能入口见 [SKILL.md](SKILL.md)。

## 直接复用的指令

> 使用 $book-case-video 制作第006期《书名》（作者），主题是“一个具体的关系问题”。资料是我提供的文件/网址。沿用中文旁白、中文主体、小标题中英双语、仅英文字幕、A版封面与无人声配乐。先核查来源与适用范围，拆解一个原创案例，校验对话口语化，然后完成带封面的MP4。保存到当前系列约定目录，附英文SRT和口语校验报告。

只做策划时，把“完成MP4”改为“只交付脚本和分镜，暂不生成语音与视频”。换用其他系列时，明确覆盖配色、语言、封面与保存位置。

## 包内内容

- `SKILL.md`：触发规则、工作流程、内容与交付要求。
- `references/prompts.md`：总控及8组阶段提示词，可独立复制到其他模型。
- `references/contracts.md`、`episode.schema.json`：输入输出与结构约束。
- `references/tools-and-runbook.md`：工具职责、环境依赖、逐步命令。
- `references/series-profile.md`：你已确认的系列偏好和保存位置。
- `scripts/pipeline.py`：validate、scaffold、voice、measure、build、render六个命令。
- `assets/project/`：可复用Remotion工程、A版HTML封面与Playwright导出脚本。
- `examples/intimate-relationships.json`：用第五期内容整理的完整结构示例，不包含第三方依赖和书籍全文。

## 交付格式

每期输入一份`episode.json`；输出带封面MP4、一份英文SRT、两种封面PNG、口语/来源报告及QA记录。
当前系列最终视频目录固定为`outputs/videos-with-covers/`；同一期新版验收后替换，旧版归档。

## 安装与限制

将整个`book-case-video`文件夹置于Codex的skills目录即可发现。安装后下一轮可用`$book-case-video`调用。其他模型可直接使用prompts与契约，不保证支持Codex特定工具。

本包提供制作骨架和提示词，不自动获得整本书，不包含在线配音额度、音乐授权或第三方依赖。格式合格不等于事实已核查；语速检查不等于真人听审。

本次验证：技能格式、输入契约、真实配音时长、封面渲染、模板构建、TypeScript、来源缺失/虚假整书范围/非法路径/待审/坏时长拦截、用户改动保护、字幕时间轴。未在此次打包测试中重新生成在线语音或渲染完整长片。

## 从 GitHub 安装

下载仓库 ZIP，将含 SKILL.md 的文件夹命名为 book-case-video，放到自己的 Codex skills 目录（通常为 ~/.codex/skills/book-case-video）。开始新会话后用 $book-case-video 调用。

也可让 Codex：使用 skill-installer 从 https://github.com/jiaxu898121-sudo/book-case-video 安装技能（仓库根目录）。

首次使用请修改 references/series-profile.md，并按 references/tools-and-runbook.md 安装依赖。README 中的第006期与目录是系列示例，可自行覆盖。示例 JSON 的来源审查记录不适用于你换入的新书，必须重新核查。

## 许可与依赖

本仓库沿用 MIT 许可证。React、Remotion、Playwright、edge-tts 等第三方依赖各自适用其许可和服务条款；本仓库许可证不授予书籍全文、音乐或合成声音的第三方权利。