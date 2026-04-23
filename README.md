# Clash 三段式配置生成工具

一个用于生成 Clash 代理配置文件的图形化工具，支持 Web 界面和浏览器扩展两种使用方式。

## 功能特点

- **三段式分流规则**：国内域名直连、国外域名走代理、特定服务走静态住宅 IP
- **静态住宅 IP 支持**：导入 SOCKS5 格式静态 IP，为指定服务分配独立线路
- **可视化操作**：拖拽上传、实时日志、配置预览、一键下载
- **双端支持**：本地 Web 服务 + Chrome 浏览器扩展
- **智能解析**：自动识别 YAML 代理列表和 TXT 格式 IP 信息

## 文件结构

```
.
├── config_generator_web.py      # Web 服务端主程序
├── chrome-extension/            # 浏览器扩展
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.css
│   ├── popup.js
│   └── generator.js
├── 启动Web界面.bat              # Windows 一键启动脚本
└── 参考数据/                    # 示例配置文件（仅供参考）
```

## 使用方法

### 方式一：Web 界面（推荐）

1. 确保已安装 Python 3.10+
2. 双击运行 `启动Web界面.bat`
3. 浏览器自动打开 `http://localhost:8888`
4. 上传代理配置和静态 IP 文件，点击生成

命令行启动：
```bash
python config_generator_web.py [端口]
```

### 方式二：Chrome 扩展

1. 打开 Chrome 浏览器，进入 `chrome://extensions/`
2. 开启右上角「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `chrome-extension` 文件夹
5. 点击浏览器工具栏图标即可使用

## 输入文件格式

### 代理配置（YAML）

标准的 Clash `proxies` 列表格式：

```yaml
proxies:
  - name: "节点1"
    type: ss
    server: example.com
    port: 443
    cipher: aes-256-gcm
    password: "密码"
  - name: "节点2"
    type: vmess
    server: 1.2.3.4
    port: 443
    uuid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    alterId: 0
    cipher: auto
```

### 静态住宅 IP（TXT）

每行一个 SOCKS5 格式：

```
用户名:密码@服务器地址:端口
```

示例：
```
user1:pass1@192.168.1.1:1080
user2:pass2@192.168.1.2:1080
```

## 输出配置说明

生成的配置文件包含以下分流规则：

| 规则类别 | 分流方式 | 说明 |
|---------|---------|------|
| 国内域名 | DIRECT | 常见国内网站和服务直连 |
| 国外域名 | 代理组 | 海外网站走代理节点 |
| 指定服务 | 静态 IP 组 | 特定平台强制走静态住宅 IP |
| 兜底规则 | 代理组 | 未命中规则的全部走代理 |

DNS 配置采用国内 + 海外双解析策略，确保分流准确性。

## 系统要求

- Python 3.10 或更高版本（Web 模式）
- Chrome / Edge 浏览器（扩展模式）
- Windows / macOS / Linux

## 注意事项

- 请妥善保管自己的服务器配置和静态 IP 信息，不要上传到公共平台
- 静态 IP 文件和代理配置仅在本地处理，不会上传至任何服务器
- 建议定期更新 GeoIP / GeoSite 数据库以获得最佳分流效果

## 许可证

MIT License
