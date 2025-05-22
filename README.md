# AutoMorse - 自动摩尔斯码解码器

AutoMorse 是一个基于 Python 的自动摩尔斯码解码器，能够实时识别和解码音频中的摩尔斯码信号。该项目使用 PyQt6 构建图形界面，结合音频处理和信号分析技术，为业余无线电爱好者和摩尔斯码学习者提供了一个实用的工具。

## 功能特点

- 实时音频采集和摩尔斯码解码
- 支持自定义音频设备选择
- 可调节的音频参数（带宽、频率等）
- 内置摩尔斯码测试音频生成器
- 支持音频文件导入和解码
- 实时频谱显示
- 自动保存和加载配置

## 系统要求

- Windows 10 或更高版本
- Python 3.8 或更高版本
- 声卡设备（支持音频输入和输出）

## 安装步骤

1. 克隆仓库：
```powershell
git clone https://github.com/yourusername/AutoMorse.git
cd AutoMorse
```

2. 创建虚拟环境（推荐）：
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. 安装依赖：
```powershell
pip install -r requirements.txt
```

## 使用方法

1. 启动程序：
```powershell
python src/main.py
```

2. 配置音频设备：
   - 在设置面板中选择输入设备（用于接收摩尔斯码信号）
   - 选择输出设备（用于播放音频）
   - 选择监听设备（用于测试音频）

3. 调整参数：
   - 音频采集带宽：调整音频信号的采集范围
   - CW编码频率：设置摩尔斯码信号的频率
   - CW模式截取带宽：设置信号分析的带宽范围

4. 开始解码：
   - 点击"开始"按钮开始实时解码
   - 使用"测试音频"功能生成测试信号
   - 导入音频文件进行离线解码

## 项目结构

```
AutoMorse/
├── src/
│   ├── main.py              # 主程序入口
│   ├── audio_manager.py     # 音频设备管理
│   ├── morse_utils.py       # 摩尔斯码工具类
│   ├── ui/
│   │   ├── main_window.py   # 主窗口界面
│   │   └── settings.py      # 设置界面
│   └── utils/
│       └── config.py        # 配置管理
├── requirements.txt         # 项目依赖
├── CHANGELOG.md            # 更新日志
└── README.md               # 项目文档
```

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新历史。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交代码前，请确保：

1. 代码符合项目的编码规范
2. 添加必要的测试用例
3. 更新相关文档
4. 提供清晰的提交信息

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至：your.email@example.com

## 致谢

感谢所有为本项目做出贡献的开发者。 