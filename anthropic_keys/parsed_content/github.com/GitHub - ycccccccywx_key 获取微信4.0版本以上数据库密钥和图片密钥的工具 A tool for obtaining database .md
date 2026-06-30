---
source: https://github.com/ycccccccy/wx_key
parsed_date: 2026-06-27 01:30:18
domain: github.com
---

Title: GitHub - ycccccccy/wx_key: 获取微信4.0版本以上数据库密钥和图片密钥的工具 | A tool for obtaining database keys and image keys for WeChat versions 4.0 and above

URL Source: https://github.com/ycccccccy/wx_key

Markdown Content:
## 微信数据库与图片密钥提取工具

[](https://github.com/ycccccccy/wx_key#%E5%BE%AE%E4%BF%A1%E6%95%B0%E6%8D%AE%E5%BA%93%E4%B8%8E%E5%9B%BE%E7%89%87%E5%AF%86%E9%92%A5%E6%8F%90%E5%8F%96%E5%B7%A5%E5%85%B7)
在微信 4.0 及以上版本中获取数据库内容与缓存图片解密密钥的工具

 Tool for obtaining WeChat database and decrypting cache image keys

[![Image 1: License](https://camo.githubusercontent.com/8bb50fd2278f18fc326bf71f6e88ca8f884f72f179d3e555e20ed30157190d0d/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d677265656e2e737667)](https://github.com/ycccccccy/wx_key/blob/main/LICENSE)[![Image 2: Platform](https://camo.githubusercontent.com/2a0bb1a881f7dddc7b12449f851d87dc64c667c1c38414077510b695b8a55969/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f706c6174666f726d2d57696e646f77732d6c69676874677265792e737667)](https://www.microsoft.com/windows)[![Image 3: Stars](https://camo.githubusercontent.com/d2848547583d1e18d1c2f2945e7e39132b6d06c38ef2e630ae1e6a3ebfb958c4/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f73746172732f7963636363636363792f77785f6b65793f7374796c653d666c6174)](https://github.com/ycccccccy/wx_key/stargazers)[![Image 4: Forks](https://camo.githubusercontent.com/3ec1b73dbd42cc2bb44b8431f809a4fd7a273dacd3ea9afb79db2a73d2c922c6/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f666f726b732f7963636363636363792f77785f6b65793f7374796c653d666c6174)](https://github.com/ycccccccy/wx_key/network/members)

[![Image 5: 应用截图](https://github.com/ycccccccy/wx_key/raw/main/app.jpg)](https://github.com/ycccccccy/wx_key/blob/main/app.jpg)

**重要声明**：本项目仅供技术研究和学习使用，严禁用于任何恶意或非法目的。

Caution

**通知：本项目即日起永久停止更新，不再回复任何issue**

如果这个项目对你有帮助，请给我一个 Star ❤️

* * *

## 项目简介

[](https://github.com/ycccccccy/wx_key#%E9%A1%B9%E7%9B%AE%E7%AE%80%E4%BB%8B)
本项目面向微信 4.0 及以上版本，用于：

获取微信数据库密钥和提取缓存图片的解密密钥

## 小小小提示

[](https://github.com/ycccccccy/wx_key#%E5%B0%8F%E5%B0%8F%E5%B0%8F%E6%8F%90%E7%A4%BA)
如果你对本项目感兴趣，也可以看看我的另一个项目：

[EchoTrace - 微信聊天记录导出与分析，年度报告应用](https://github.com/ycccccccy/echotrace)

## 关于支持版本的说明

[](https://github.com/ycccccccy/wx_key#%E5%85%B3%E4%BA%8E%E6%94%AF%E6%8C%81%E7%89%88%E6%9C%AC%E7%9A%84%E8%AF%B4%E6%98%8E)
支持所有微信 4.x 版本

*   已实际测试版本： 
    *   4.1.5.11
    *   4.1.4.17
    *   4.1.4.15
    *   4.1.2.18
    *   4.1.2.17
    *   4.1.0.30
    *   4.0.5.17

## 快速开始

[](https://github.com/ycccccccy/wx_key#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)
1.   **下载发布版本**
    *   前往 [Releases](https://github.com/ycccccccy/wx_key/releases) 页面，下载最新的压缩包 `app.zip`。

2.   **运行工具**
    *   解压后运行其中的 `wx_key.exe`，或运行你自行编译得到的可执行文件。

> **注意**：请不要把工具文件夹放在任何包含中文字符的目录下，否则可能导致 DLL 加载失败等问题。

### 图片密钥获取建议流程

[](https://github.com/ycccccccy/wx_key#%E5%9B%BE%E7%89%87%E5%AF%86%E9%92%A5%E8%8E%B7%E5%8F%96%E5%BB%BA%E8%AE%AE%E6%B5%81%E7%A8%8B)
1.   彻底关闭当前登录的微信
2.   重新启动微信并登录
3.   打开朋友圈寻找带图片的
4.   点击图片，再点击右上角打开大图
5.   重复几次3和4，大概2-3次即可
6.   迅速回到工具内获取图片密钥

## 目录结构概览

[](https://github.com/ycccccccy/wx_key#%E7%9B%AE%E5%BD%95%E7%BB%93%E6%9E%84%E6%A6%82%E8%A7%88)

```
wx_key/
├── lib/                                  # Flutter 前端
│   ├── main.dart                         # UI 与状态管理
│   ├── services/
│   │   ├── remote_hook_controller.dart   # FFI 控制器，轮询 DLL
│   │   ├── dll_injector.dart             # WeChat 启动/进程控制
│   │   ├── key_storage.dart              # 密钥持久化
│   │   ├── image_key_service.dart        # 图片密钥提取
│   │   └── app_logger.dart / log_reader.dart
│   └── widgets/                          # 自定义组件
├── assets/dll/wx_key.dll                 # 控制器 DLL
├── wx_key/                               # C++ 原生项目（Visual Studio）
│   ├── include/                          # Hook、IPC、Shellcode 头文件
│   ├── src/                              # hook_controller、remote_scanner 等实现
│   └── wx_key.vcxproj                    # 工程配置
└── build/windows/...                     # Flutter 构建产物
```

## DLL 扩展使用

[](https://github.com/ycccccccy/wx_key#dll-%E6%89%A9%E5%B1%95%E4%BD%BF%E7%94%A8)
如果你希望在自定义程序中直接复用 `wx_key.dll`（例如：

*   自行获取 WeChat 进程 PID
*   调用 DLL 导出函数以获取密钥

参考文档：[`docs/dll_usage.md`](https://github.com/ycccccccy/wx_key/blob/main/docs/dll_usage.md)，里面包含：

*   DLL 导出接口说明
*   调用示例
*   常见注意事项与错误排查

## 开发构建

[](https://github.com/ycccccccy/wx_key#%E5%BC%80%E5%8F%91%E6%9E%84%E5%BB%BA)
如果你希望自行编译项目，可以按照以下步骤：

# 1. 克隆项目
git clone https://github.com/ycccccccy/wx_key.git
cd wx_key

# 2. 安装依赖
flutter pub get

# 3. 构建发布版本（Windows）
flutter build windows --release

# 4. 可执行文件位置
# build/windows/runner/Release/wx_key.exe

## 许可证与免责声明

[](https://github.com/ycccccccy/wx_key#%E8%AE%B8%E5%8F%AF%E8%AF%81%E4%B8%8E%E5%85%8D%E8%B4%A3%E5%A3%B0%E6%98%8E)
### 许可证

[](https://github.com/ycccccccy/wx_key#%E8%AE%B8%E5%8F%AF%E8%AF%81)
本项目采用 **MIT License**，详见 [LICENSE](https://github.com/ycccccccy/wx_key/blob/main/LICENSE) 文件。

 你可以自由使用、修改和分发本软件，但需要保留原有版权声明和许可证文本。

### 免责声明

[](https://github.com/ycccccccy/wx_key#%E5%85%8D%E8%B4%A3%E5%A3%B0%E6%98%8E)
> **重要提醒**：本工具仅用于技术研究和学习目的。

*   使用本工具产生的一切后果与责任，均由使用者自行承担
*   开发者不对因使用本工具而导致的任何损失负责
*   使用者必须确保其行为符合当地法律法规
*   严禁将本工具用于任何商业或恶意用途

## 贡献指南

[](https://github.com/ycccccccy/wx_key#%E8%B4%A1%E7%8C%AE%E6%8C%87%E5%8D%97)
欢迎通过 Issue / Pull Request 来改进本项目：

1.   Fork 本仓库
2.   创建分支：`git checkout -b feature/YourFeature`
3.   提交更改：`git commit -m "Add YourFeature"`
4.   推送分支：`git push origin feature/YourFeature`
5.   发起 Pull Request 并附上说明

## 致谢

[](https://github.com/ycccccccy/wx_key#%E8%87%B4%E8%B0%A2)
感谢以下项目提供启发与思路：

*   [WxDatDecrypt](https://github.com/recarto404/WxDatDecrypt) — 提供了关键的 imagekey 获取思路

## Star History

[](https://github.com/ycccccccy/wx_key#star-history)
[![Image 6: Star History Chart](https://camo.githubusercontent.com/b6c22697f8aa89196967be98798e1740f81283c4d1ffd8c8dd1de6121f8d968a/68747470733a2f2f6170692e737461722d686973746f72792e636f6d2f7376673f7265706f733d7963636363636363792f77785f6b657926747970653d64617465266c6567656e643d746f702d6c656674)](https://www.star-history.com/#ycccccccy/wx_key&type=date&legend=top-left)

* * *

**请负责任地使用本工具，遵守相关法律法规**

 Made for educational purposes ❤️
