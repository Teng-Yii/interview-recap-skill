# 音视频输入

基础文字模式无需安装音频依赖。需要音视频时：Python 3.10+、ffmpeg，以及 `python3 -m pip install -r requirements-audio.txt`。macOS可自行安装ffmpeg；其他系统使用各自包管理器。命令中的python3在部分Windows环境需换成python。

```sh
python3 scripts/transcribe.py /path/to/interview.m4a --output /path/to/private/transcription
python3 scripts/prepare.py /path/to/private/transcription/transcript.tsv --output /path/to/private/review
```

`--output`必须是尚不存在的新目录。默认medium、CPU/int8、中文。首次使用需要从模型托管站下载模型，后续可用`--offline`仅使用缓存；`--model`也接受本地模型目录。可按硬件调整device与compute-type，不默认安装GPU驱动。

输出TXT、TSV、SRT；临时16kHz WAV仅在本次任务临时目录使用并清理，不删除用户原文件或最终转写。失败时`.partial`不是完整转写，应检查原因后选择新目录重跑。脚本不上传录音到转写API；但后续在Agent里复盘时，提供给Agent的文本可能由其模型服务处理，请按所用Agent的配置判断。

转写不包含可靠的说话人分离，也不会自动知道公司、轮次或面试结果。需要时先校对说话人、专业术语，再分析。不要根据没有检测到某个词就认定用户没回答。没有原始画面时，不评价白板或代码编写是否正确。
