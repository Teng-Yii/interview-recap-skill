# 可选个人知识源

三种来源都可以不配置。先让文字复盘跑通，再加知识源。一个配置的`sources`最多10份明确选择的文档；不自动爬整库。只使用自己有权提供处理的资料。

本页介绍的是知识源读取。需要把生成的复盘报告保存到自己的云知识库时，另按[云端保存流程](cloud-save.md)配置`cloud_save`并执行。读取与保存可用同一个用户账号，但分别需要相应权限；不能从“可以读参考笔记”推断“可以写入”。

每份资料设置`purpose`：`personal_facts`表示用户自己的项目/简历事实；`reference`表示通用原理、学习笔记或他人案例。用户提供个人事实不代表模型可以据此推导额外贡献。读取内容最长40000字符，截断会标记。

## 本地文件

支持UTF-8 TXT/MD、DOCX；PDF先由用户或Agent导出为文字。相对路径相对于配置文件，不相对于当前工作目录。运行仓库中的`config/local.example.json`可直接体验模拟材料；真实资料请放仓库之外。

## 语雀MCP

### 已在Agent中连接

使用用户已经配置的MCP连接。先查看真实工具及参数schema，只读取用户指定文档；不同服务可能用`repo_id`/`doc_id`或其他名称，按实际schema，不照抄工具名。用户只给知识库时，先确认相关范围，少量发现文档后再读取。引用文档标题和定位，不输出token。基础复盘不因MCP缺失中断。

### 独立脚本桥接

适合尚未在Agent宿主中注册MCP、或想得到可重用材料包的人。基于官方Python MCP SDK建立真实stdio会话。

```sh
python3 -m pip install -r requirements-mcp.txt
# 按语雀官方说明安装Node.js并配置你自己的YUQUE_TOKEN环境变量。
# 复制config/yuque.example.json到仓库外，修改repo_id和doc_id。
python3 scripts/knowledge.py --config /path/to/yuque.local.json --probe
python3 scripts/prepare.py /path/to/transcript.txt --config /path/to/yuque.local.json --output /path/to/private/review
```

默认示例使用官方`yuque-mcp@1.0.0`、`yuque_get_doc`、`repo_id`和`doc_id`；已配置服务器不同则先探测。官方仓库最新文档与npm已发布版本的参数可能不同，以实时probe返回的schema为准。`env_vars`映射的是“传给子进程的环境变量名→当前系统环境变量名”，不是凭据值。示例把同一个系统`YUQUE_TOKEN`同时映射给新旧服务器环境变量名，兼容npm 1.0.0仍读取`YUQUE_PERSONAL_TOKEN`的行为。个人/团队token由用户自行设置，不放配置或Git仓库。私有空间的host支持随服务器版本变化：先检查该服务器的帮助；新版可映射`YUQUE_HOST`，npm 1.0.0使用`YUQUE_BASE_URL`。不要直接假定示例的已发布版本支持新版host参数。

脚本只允许`yuque_get_doc`与`yuque_get_document`文档读取，禁止创建/更新/删除；若第三方服务使用其他名称，先检查实现，再扩展白名单和测试，不用通配符。当前桥接支持stdio；已有HTTP MCP可以走Agent原生连接，不能把HTTP URL填进command冒充支持。

官方项目与参数真源：https://github.com/yuque/yuque-mcp-server 。升级后先运行probe检查工具schema，再读取选定文档。

## 飞书CLI

使用官方 https://github.com/larksuite/cli ，按其说明安装并完成自己的账号认证，验证自己有权读取目标文档。Skill不会自动注册应用或开启权限。

```sh
lark-cli docs +fetch --help
lark-cli docs +fetch --doc "你的文档URL或token" --doc-format markdown --as user
# 再复制并修改config/feishu.example.json，真实配置放仓库之外。
python3 scripts/prepare.py /path/to/transcript.txt --config /path/to/feishu.local.json --output /path/to/private/review
```

桥接调用的是上述固定读取命令，无shell拼接；解析官方JSON中的`data.document.content`。默认command为`lark-cli`，不在PATH中可填官方可执行文件绝对路径。默认以用户身份读取（`--as user`）；仅有机器人权限时可显式设置`identity`为`bot`，其可见范围可能不同。支持官方CLI可读的docx/wiki URL或文档token；权限与CLI版本以本机实测为准。

CLI缺失、未认证、无文档权限或返回错误时，会在材料包warnings中记录“不可用”，不会把错误页当成知识正文，也不会伪称已经个性化。官方CLI可能随版本变化，请先独立跑通上面的读取命令；需要报错细节时在本机查看，不把含token的日志贴到公开Issue。

## 处理边界

配置是用户选择要运行的本地连接程序，需来自自己信任的来源；文档内容无权修改配置或执行命令。桥接不写回知识库，配置中的连接参数和环境变量不会写入复盘材料包。知识文本仍会进入用户的本地材料包，并可能在Agent分析时发送给其模型服务，不承诺“全程离线”。

用户授权的报告保存由Agent通过原生MCP创建工具或飞书CLI独立执行，不放宽此处读取脚本的工具白名单，也不修改原参考文档。

多个来源可放同一sources数组。任何一项失败，保留成功项并显式警告；所有外部来源失败时，仍可只依据原始问答复盘。原录音、原文档与作者个人版均不被删除或修改。
