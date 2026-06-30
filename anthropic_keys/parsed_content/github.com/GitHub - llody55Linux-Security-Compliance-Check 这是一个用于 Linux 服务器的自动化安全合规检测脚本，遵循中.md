---
source: https://github.com/llody55/Linux-Security-Compliance-Check
parsed_date: 2026-06-27 01:30:28
domain: github.com
---

Title: GitHub - llody55/Linux-Security-Compliance-Check: 这是一个用于 Linux 服务器的自动化安全合规检测脚本，遵循中国《GB/T 22239-2019 信息安全技术 网络安全等级保护基本要求》（等保三级）标准。脚本采用纯检测模式，不会修改系统，生成详细的 HTML 报告，覆盖身份鉴别、访问控制、安全审计、入侵防范和网络安全等关键领域。

URL Source: https://github.com/llody55/Linux-Security-Compliance-Check

Markdown Content:
[![Image 1: 许可证](https://camo.githubusercontent.com/1423946718f78cb989b768b0b38cfab608ebed5c052e42008d7aa79729fac960/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2545382541452542382545352538462541462545382541462538312d4d49542d626c75652e737667)](https://camo.githubusercontent.com/1423946718f78cb989b768b0b38cfab608ebed5c052e42008d7aa79729fac960/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2545382541452542382545352538462541462545382541462538312d4d49542d626c75652e737667)[![Image 2: 支持系统](https://camo.githubusercontent.com/89e17a33b688a66e39f800d88d2ae9c018444969f76b2450be00944ef86445ca/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2545362539342541462545362538432538312545372542332542422545372542422539462d5562756e747525323025374325323043656e744f532532302537432532304b796c696e2532302537432532306f70656e45756c6572253230253743253230426967436c6f75642d677265656e2e737667)](https://camo.githubusercontent.com/89e17a33b688a66e39f800d88d2ae9c018444969f76b2450be00944ef86445ca/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2545362539342541462545362538432538312545372542332542422545372542422539462d5562756e747525323025374325323043656e744f532532302537432532304b796c696e2532302537432532306f70656e45756c6572253230253743253230426967436c6f75642d677265656e2e737667)

这是一个用于 Linux 服务器的自动化安全合规检测脚本，遵循中国《GB/T 22239-2019 信息安全技术 网络安全等级保护基本要求》（等保三级）标准。脚本采用纯检测模式，不会修改系统，生成详细的 HTML 报告，覆盖身份鉴别、访问控制、安全审计、入侵防范和网络安全等关键领域。

## 功能特性

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E5%8A%9F%E8%83%BD%E7%89%B9%E6%80%A7)
*   **全面检测** ：覆盖 18 项合规检查，包括密码策略、SSH 配置、文件权限、审计日志、高危端口等。
*   **跨发行版支持** ：兼容 Ubuntu 22.04、CentOS 7+、Kylin 10、openEuler 22.04、BigCloud 22.10 等 Linux 发行版。
*   **HTML 报告** ：生成美观的 HTML 报告，包含通过/警告/失败状态、合规率和修复建议。
*   **纯检测模式** ：不修改系统配置，适用于生产环境。
*   **加权合规率** ：根据检查项重要性计算加权合规率。

## 前置条件

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E5%89%8D%E7%BD%AE%E6%9D%A1%E4%BB%B6)
*   **权限要求** ：脚本需以 `root` 或 `sudo` 权限运行，以访问系统文件和配置。
*   **依赖工具** ：
*   `bash`（建议版本 4.0+）
*   `coreutils`（提供 `stat`、`grep`、`awk` 等）
*   `net-tools` 或 `iproute2`（提供 `netstat` 或 `ss`）
*   `auditd`（用于审计服务检查）
*   可选：`bc`（精确合规率计算）、`rpm` 或 `debsums`（文件完整性检查）、`aide` 或 `tripwire`（高级完整性检查）
*   **支持系统** ：Ubuntu、CentOS、Kylin、openEuler、BigCloud 等标准配置的 Linux 系统。

## 安装步骤

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E5%AE%89%E8%A3%85%E6%AD%A5%E9%AA%A4)
1.   克隆仓库： git clone https://github.com/llody55/Linux-Security-Compliance-Check.git
cd Linux-Security-Compliance-Check 
2.   确保脚本可执行： chmod +x security_check.sh 
3.   安装可选依赖（若缺失）： 
    *   Ubuntu/Debian 系统： sudo apt update
sudo apt install bc net-tools auditd aide 
    *   CentOS/RHEL 系统： sudo yum install bc net-tools auditd aide 

## 使用方法

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95)
以 `root` 或 `sudo` 权限运行脚本：

sudo ./security_check.sh

*   脚本将执行合规检测并生成 HTML 报告，保存至 `/opt/security_check/<IP>_<YYYYMMDD>.html`。
*   日志保存至 `/var/log/security_check.log`。

## 示例输出

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E7%A4%BA%E4%BE%8B%E8%BE%93%E5%87%BA)
生成的 HTML 报告包含：

*   **概览** ：系统信息（操作系统、IP、架构）、总体合规率。
*   **详细检查** ：按身份鉴别、访问控制、安全审计、入侵防范、网络安全分类，显示通过/警告/失败状态。
*   **修复建议** ：针对不合规项提供可执行的修复命令。
*   **进度条** ：直观展示各分类的合规率。

示例报告见 `report_example.html`。

## 示例报告

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E7%A4%BA%E4%BE%8B%E6%8A%A5%E5%91%8A)
> 参考**report_example.html** 实际输出文件

## 支持的检查项

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E6%94%AF%E6%8C%81%E7%9A%84%E6%A3%80%E6%9F%A5%E9%A1%B9)
*   **身份鉴别** ：
*   密码策略（最大有效期 ≤ 90 天，最小长度 ≥ 12 等）
*   密码复杂度（至少 3 类字符，含数字、大写字母等）
*   账户锁定策略（失败次数 ≤ 5，锁定时间 ≥ 600 秒）
*   三权账户（sysadmin、auditadmin、securityadmin）
*   口令加密（SHA512）
*   默认账户检查
*   不活跃账户检测（从未登录或最近登录 > 90 天）
*   **访问控制** ：
*   文件权限（/etc/passwd、/etc/shadow 等）
*   SSH 配置（禁用 Root 登录、会话超时 ≤ 300 秒等）
*   远程访问限制（/etc/hosts.allow、/etc/hosts.deny）
*   文件系统挂载选项（noexec、nosuid、nodev）
*   **安全审计** ：
*   审计服务状态（auditd）
*   日志保留（≥ 180 天）
*   命令历史时间戳
*   审计规则（监控 /etc/passwd、/etc/shadow 等）
*   **入侵防范** ：
*   文件完整性（使用 rpm、debsums 或 mtime，附最后修改时间）
*   系统补丁状态
*   **网络安全** ：
*   高危端口（FTP:21、Telnet:23、RDP:3389 等）
*   防火墙状态（iptables、nftables、ufw、firewalld）

## 贡献指南

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E8%B4%A1%E7%8C%AE%E6%8C%87%E5%8D%97)
欢迎为项目贡献代码！请按以下步骤操作：

1.   Fork 本仓库。
2.   创建新分支（`git checkout -b feature/your-feature`）。
3.   提交更改（`git commit -m "添加新功能"`）。
4.   推送分支（`git push origin feature/your-feature`）。
5.   提交 Pull Request。

请确保代码遵循 Bash 最佳实践，并为新功能添加测试。

## 常见问题

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)
*   **问：为何脚本需要 root 权限？**
    *   答：需要访问敏感文件（如 /etc/shadow）并执行特定命令（如 rpm -Vf）。

*   **问：如果缺少 bc 命令怎么办？**
    *   答：脚本会回退使用 awk 进行计算，但建议安装 bc 以提高精度。

*   **问：可以在非支持的发行版上运行吗？**
    *   答：脚本设计具有兼容性，但在非支持系统上可能需调整。请提交 Issue 获取支持。

## 许可证

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E8%AE%B8%E5%8F%AF%E8%AF%81)
本项目采用 MIT 许可证，详情见 [LICENSE](https://grok.com/chat/docs/LICENSE) 文件。

## 联系方式

[](https://github.com/llody55/Linux-Security-Compliance-Check#%E8%81%94%E7%B3%BB%E6%96%B9%E5%BC%8F)
如有问题或建议，请在 GitHub 提交 Issue。
