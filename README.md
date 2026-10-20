# 面试复盘 Skill

把真实或模拟面试中的回答整理成有原话依据的反馈、准备清单和下一次练习。支持文字直接复盘、本地音视频转写，以及可选的个人简历、语雀MCP、飞书CLI知识增强。

**没有语雀或飞书账号也能用。** 这是给Agent使用的Skill，配有材料整理脚本；不是双击即运行的网页，也不是小程序。基础文字模式不需要额外模型API Key，分析使用你自己的Agent及其模型服务，相关额度/费用依服务而定。

## 安装与第一次使用

1. 下载本仓库Release中的`interview-recap-skill-v0.1.0.zip`并解压，得到`interview-recap`文件夹。
2. 将整个文件夹放入Agent支持的skills目录。Codex可使用`~/.agents/skills/interview-recap/`或`~/.codex/skills/interview-recap/`；Claude Code可使用`~/.claude/skills/interview-recap/`。已有同名个人版时，先备份并选择项目级安装，避免覆盖。其他Agent按其技能安装说明操作。
3. 重新加载技能后，让Agent使用`interview-recap`复盘你提供的问答。不同宿主的触发方式不同，也可直接让Agent读取`SKILL.md`。

可以直接说：

> 使用面试复盘Skill。以下是我的模拟回答：面试官问“你怎么证明缓存优化有效”，我回答“应该快很多，但没测过”。请引用原句指出缺口，不补造数据，给出下一步验证方法。我没有简历和个人知识库。

Agent应该指出“效果没有测量依据”，帮助你准备可比的测试，而不是替你写“耗时下降80%”。

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

语雀和飞书可以同时配置，也可以都不配置。脚本只读取明确选定的文档；读取失败会记录警告，基础复盘继续，不冒充已经读取。没有内置用户Token、文档ID或作者私人资料。

## 报告会交付什么

- 实际问题与回答，带原有时间戳或文本证据编号。
- 回答中具体的表达缺失、技术疑点与待确认事实。
- 基于已提供经历的重组提纲；缺少的事实列为待补，不凭空生成事故、指标或贡献。
- 标明是新练习的连续追问，以及最多三个下一次准备事项。
- 提供简历时才给简历对照建议；附读取范围和校对事项。

不预测录用结果，不按一个分数定义能力。使用前确认自己有权处理材料；录音转写在本地运行，但Agent分析可能调用云端模型，不承诺全流程离线。不会自动将个人资料发布到GitHub、语雀或飞书，也不会写入作者记忆。输出和转写由用户保管，本Skill不自动删除原材料。

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
- 版本下载：https://github.com/Teng-Yii/interview-recap-skill/releases/latest
- 作者：一腾。公众号：一腾的成长笔记。

MIT License，见[LICENSE](LICENSE)。本仓库不分发第三方CLI、MCP服务器或模型权重；各自许可与使用条件以其项目为准。
