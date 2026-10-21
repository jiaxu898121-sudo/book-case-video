# 工具、依赖与可执行流程

## 工具职责

| 环节 | 首选 | 输出/限制 |
|---|---|---|
| 查书与来源 | 用户文件、浏览工具、出版社/作者/原始论文 | 只记录实际读到的范围；不要求GitHub才能查书 |
| 研究内容提炼、案例、口语与翻译复核 | 当前语言模型 | 使用prompts.md；这些语义工作不能由JSON验证器代替 |
| 文件 | Python 3.10+、pathlib、JSON | UTF-8；命令使用参数列表，不拼shell指令 |
| 合成配音 | 已授权TTS；脚本默认edge-tts预设中文声音 | 依赖网络服务；可能不可用，无离线/商业许可保证；可改用其他TTS并保存同名音频 |
| 合同验证 | Python jsonschema | pip安装需正常授权，不自动升级系统Python |
| 时序 | ffprobe | 按真实音频长度，不凭字数假定成片时长 |
| 动画与导出 | Node.js、React、Remotion | 包内版本固定为本系列使用的版本；不保证永远最新 |
| 封面 | HTML/CSS、Playwright、浏览器 | 字体依赖本地微软雅黑/Arial；其他机器须准备可用字体并重查排版 |
| 音视频检查 | ffprobe、FFmpeg、浏览器、实际视听 | 简化FFmpeg构建可能缺滤镜；别将不支持的过滤器命令写成已通过 |

GitHub用于发现/检查技能与代码，不是书籍事实的默认来源。Remotion技能可辅助API细节；本包不复制其整套文档。没有相同插件时，使用可用的文件、浏览与脚本工具。

## 复用方式

1. 复制examples/intimate-relationships.json到当期独立工作目录，改为自己的书与来源。先完成研究、口语与翻译复核；不要仅为运行脚本把reviews改为passed。
2. 安装Python依赖（需要时在独立环境）：`python -m pip install jsonschema edge-tts`。本包不包含第三方依赖或凭据。
3. 执行 `python scripts/pipeline.py validate episode.json --ready`。
4. 配音（仅在允许在线服务并确认文本后）：`python scripts/pipeline.py voice episode.json`。预设声线例如zh-CN-YunxiNeural、zh-CN-XiaoxiaoNeural。它会比对台词、voice和rate的指纹，保留未变动音频。其他TTS输出保存为voice/scene-id-line-id.mp3。
5. 测量：`python scripts/pipeline.py measure episode.json --ffprobe <ffprobe路径>`。
6. 建立空的专用工程：`python scripts/pipeline.py scaffold episode.json --project 当期目录/project`。只复制模板，不访问网络。
7. 在该工程按package.json安装依赖，然后生成封面：`node tools/render-cover.mjs ../episode.json .. 浏览器绝对路径`。此命令使用同目录cover.html，输出两张PNG至当期目录。Windows若pnpm符号链接失败，可用npm普通安装方式；不要改系统权限来绕过。
8. 构建：`python scripts/pipeline.py build episode.json --project 当期目录/project`。目标须为空或本工具已有工程；生成文件被手改时停止，先保留/合并用户修改。
9. 预览：`node node_modules/@remotion/cli/remotion-cli.js studio src/index.tsx --no-open`，打开实际打印URL的BookCaseVideo合成。检查最长文字/字幕及各个场景。
10. 导出：`python scripts/pipeline.py render episode.json --project 当期目录/project --delivery 最新成片目录 --node <node路径> --browser <浏览器路径> --ffmpeg <ffmpeg路径> --ffprobe <ffprobe路径>`。使用现有Edge/Chrome时指定browser会采用新版headless。
11. 脚本先渲染临时文件，验证后才归档旧版并替换正式文件。检查qa-frame-*和实际声音，将qa.json里的visual_review/listening_review如实更新；没有实际检查的字段保持pending。

浏览器、FFmpeg与Node的路径来自运行环境发现；不要把本包作者机器路径复制到其他用户环境。Remotion可能自带相应平台compositor目录中的ffmpeg.exe/ffprobe.exe；使用前确认文件存在。

## 完成标准

交付路径实际存在、成片可解码、有正确音轨与封面、期数书名一致、SRT含封面偏移、案例不冒充原书、口语校验报告可追溯。无音乐/无法合成/未导出等状态应明确说明。验收失败保留已完成产物并修复，不重复全部任务。

## 脚本边界

此工具包是可复用制作骨架，不自带所有书的正文，也不自动判断一项研究是否成立。最可靠的默认仍然是先查来源、编案例和审口语，再用脚本负责时序与工程一致性。更复杂的动效可以在保留用户改动的前提下扩展模板。

内置模板已经固定校验为720×1280、30fps；改变分辨率或帧率前需同时调整坐标、字体、安全区与模板检查，不仅改一个JSON数值。
