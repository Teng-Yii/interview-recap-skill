# 面试复盘 Skill

把真实或模拟面试中的回答整理成有原话依据的反馈、准备清单和下一次练习。支持文字直接复盘、本地音视频转写，以及可选的个人简历、语雀MCP、飞书CLI知识增强。报告完成后，还可以保存到你自己的语雀知识库或飞书云文档；固定目标授权一次，后续可自动归档并返回链接。

## 一句话让你的 Agent 安装（推荐）

把下面这一句话复制给 Codex、Claude Code 或其他支持本地工具和技能安装的 Agent：

> 请帮我安装这个面试复盘 Skill：https://github.com/Teng-Yii/interview-recap-skill ，按你当前 Agent 的技能安装方式完成安装，保留已有同名技能，并用仓库里的模拟问答跑通一次基础复盘。

Agent 会按自己的环境选择安装位置，安装后用内置模拟问答验证。你不需要先手动找技能目录、下载ZIP，或配置语雀和飞书。**请在能下载文件、写入本地技能目录的Agent中使用；普通网页聊天窗口不一定具备安装能力。**

如果Agent需要安装步骤，让它继续读取[安装与首次验证说明](references/installation.md)。同名个人版先保留，避免覆盖。宿主若需下一轮对话或重新加载才能发现新技能，按其提示操作；也可以先让Agent直接读取已安装的`SKILL.md`完成样例。

## 安装后怎么用

第一轮可以直接把问题和自己的回答发给Agent：

> 使用面试复盘Skill。面试官问“你怎么证明缓存优化有效”，我回答“应该快很多，但没测过”；请引用原句指出缺口，不补造数据，给出下一步验证方法，我没有简历和个人知识库。

也可以把自己的文字文件、录音或视频路径交给Agent，让它按Skill处理。先跑文字即可；音视频需要额外转写依赖，语雀和飞书是可选增强，等需要时再由Agent协助配置。登录、授权或环境缺失时，Agent应说明需要你完成什么，不能伪称已经装好或读过资料。

**没有语雀或飞书账号也能用。** 基础文字模式不需要额外模型API Key，分析使用你自己的Agent及其模型服务，额度和费用依服务而定。Skill不是双击即运行的网页或小程序。

## 手动安装（备用）

1. 下载[当前 main 分支的完整 Skill 压缩包](https://github.com/Teng-Yii/interview-recap-skill/archive/refs/heads/main.zip)并解压，将最外层的`interview-recap-skill-main`文件夹改名为`interview-recap`。已有版本发行包也可从[Releases](https://github.com/Teng-Yii/interview-recap-skill/releases)获取；本页当前流程以 main 分支为准。
2. 将整个文件夹放入Agent支持的skills目录。Codex可使用`~/.agents/skills/interview-recap/`或`~/.codex/skills/interview-recap/`；Claude Code可使用`~/.claude/skills/interview-recap/`。已有同名技能时保留原版，选择项目级安装或先确认替换方式。其他Agent按其技能安装说明操作。
3. 按宿主要求重新加载或在下一轮对话使用技能；未自动识别时，让Agent直接读取安装目录里的`SKILL.md`。

## 跑一个完整公开样例

在本文件所在目录运行，需要Python 3.10+。所有样例为模拟，不来自作者、客户或真实面试。

```sh
python3 scripts/prepare.py examples/interview.txt --output ../recap-demo
```

然后让Agent读取新目录中的`review-brief.md`和`review-input.json`，按本Skill生成`review.md`。**prepare成功只表示材料已整理，报告还需要Agent分析。**

增加模拟简历和项目事实：

```sh
python3 scripts/prepare.py examples/interview.txt --resume examples/resume.md --config config/local.example.json --output ../recap-demo-personalized
```

[查看这组模拟输入的复盘示例](examples/review-example.md)。

输出目录必须尚不存在，原文件不会被修改。真实材料放在仓库之外。支持TXT/MD、SRT、转写脚本生成的TSV；简历和本地知识支持TXT/MD/DOCX，PDF先导出文字。已有问答文字时不需要ffmpeg或faster-whisper。

## 可选增强

| 需求 | 使用方式 |
|---|---|
| 音频或视频 | 安装ffmpeg与`requirements-audio.txt`，按[音视频说明](references/audio.md)转写后复盘 |
| 个人简历 | `prepare.py --resume <文件>`；仅对照，不自动修改 |
| 本地项目笔记 | `--config`指定自己选择的文件，示例见`config/local.example.json` |
| 语雀MCP | 已连接的Agent可直接用；独立桥接需`requirements-mcp.txt`，配置见[知识源说明](references/knowledge-sources.md) |
| 飞书CLI | 用户自行安装并认证官方`@larksuite/cli`，读取指定文档；同见知识源说明 |
| 保存复盘到云端 | Agent通过自己的语雀MCP或飞书CLI创建笔记、读回核对并返回链接；见[云端保存](references/cloud-save.md) |

语雀和飞书可以同时配置，也可以都不配置。脚本只读取明确选定的文档；读取失败会记录警告，基础复盘继续，不冒充已经读取。没有内置用户Token、文档ID或作者私人资料。

## 自动保存到自己的语雀或飞书

配置好自己的语雀 MCP 或完成飞书 CLI 登录后，可以直接对 Agent 说：

> 使用面试复盘 Skill 处理这份录音，生成报告后保存到我指定的语雀知识库，最后给我文档链接。

或者一次设置后持续使用：

> 以后面试复盘完成后，都自动保存到我的飞书个人云空间，保留本地报告，最后给我文档链接。

Agent 会先生成报告，再用你自己的连接新建云端文档，读回核对后返回链接。也可指定飞书文件夹或 Wiki 父节点；只提供用于参考的项目笔记，不会自动覆盖它。

配置示例：[`语雀保存`](config/cloud-save.yuque.example.json)、[`飞书保存`](config/cloud-save.feishu.example.json)。`cloud_save`由Agent读取执行，支持`off`、`ask`、`auto`；`auto`用于你已经明确授权的固定保存范围。真实配置放在仓库之外，Token保留在自己的MCP或CLI认证中。[查看完整配置与保存流程](references/cloud-save.md)。

云端保存需要当前Agent具备相应MCP/CLI调用能力及目标写权限；`prepare.py`仍只负责准备复盘材料。没有云知识库也能正常使用本地复盘。

## 报告会交付什么

- 实际问题与回答，带原有时间戳或文本证据编号。
- 回答中具体的表达缺失、技术疑点与待确认事实。
- 基于已提供经历的重组提纲；缺少的事实列为待补，不凭空生成事故、指标或贡献。
- 标明是新练习的连续追问，以及最多三个下一次准备事项。
- 提供简历时才给简历对照建议；附读取范围和校对事项。

不预测录用结果，不按一个分数定义能力。使用前确认自己有权处理材料；录音转写在本地运行，但Agent分析可能调用云端模型，不承诺全流程离线。只有获得你的保存授权后，才将完成的报告存到你指定的云端位置；不上传到作者账号、不公开发布到GitHub、不自动修改知识源或写入作者记忆。输出和转写由用户保管，本Skill不自动删除原材料。

## 开发和验证

```sh
python3 -m unittest discover -s tests -v
# 可选MCP协议集成测试：
python3 -m pip install -r requirements-mcp.txt
python3 -m unittest discover -s tests -v
```

不装MCP依赖时，MCP传输测试会明确跳过。测试中的MCP服务与CLI夹具为模拟；它们验证调用、解析与失败降级，不能替代真实账号实读。真实验证范围、系统和依赖版本见[验证记录](references/verification.md)。

问题反馈请只提交可公开的最小模拟输入和脱敏错误信息，不提交Token、原始录音、真实简历或客户文档。首次发布由macOS验证，其他平台以CI和实际运行结果为准。

## 获取与许可

- GitHub：https://github.com/Teng-Yii/interview-recap-skill
- 当前完整Skill下载：https://github.com/Teng-Yii/interview-recap-skill/archive/refs/heads/main.zip
- 历史版本：https://github.com/Teng-Yii/interview-recap-skill/releases
- 作者：一腾。公众号：一腾的成长笔记。

MIT License，见[LICENSE](LICENSE)。本仓库不分发第三方CLI、MCP服务器或模型权重；各自许可与使用条件以其项目为准。
