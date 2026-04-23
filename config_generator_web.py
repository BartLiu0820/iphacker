#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash三段式配置生成工具 - Web可视化版本
"""

import re
import os
import sys
import json
import base64
import time
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# YAML特殊字符集合，需要引号包裹
_YAML_SPECIAL_CHARS = {':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'", '~'}

# 国内域名后缀列表
_CN_DOMAINS = [
    "cn", "baidu.com", "bdstatic.com", "bdimg.com",
    "qq.com", "tencent.com", "weixin.qq.com", "qpic.cn", "qlogo.cn",
    "taobao.com", "tmall.com", "alicdn.com", "aliyun.com", "alipay.com",
    "alibaba.com", "alimama.com", "1688.com", "jd.com", "jdpay.com",
    "bilibili.com", "hdslb.com", "acfun.cn", "iqiyi.com", "youku.com",
    "sina.com", "sinaimg.cn", "weibo.com", "weibocdn.com",
    "163.com", "126.com", "126.net", "127.net", "netease.com", "ydstatic.com",
    "sohu.com", "sogou.com", "sogoucdn.com",
    "ifeng.com", "ctrip.com", "dangdang.com", "douban.com",
    "zhihu.com", "douyin.com", "iesdouyin.com", "bytedance.com",
    "csdn.net", "oschina.net", "jianshu.com", "cnblogs.com",
    "meituan.com", "dianping.com", "ele.me", "amap.com", "autonavi.com",
    "360.cn", "360.com", "360safe.com", "360buyimg.com",
    "baiducontent.com", "shifen.com", "nuomi.com", "hao123.com",
    "sm.cn", "uc.cn", "alibabausercontent.com", "mmstat.com",
    "xiami.com", "xiami.net", "dingtalk.com", "alibaba-inc.com",
    "cainiao.com", "cainiao.com.cn",
    "unionpay.com", "bankcomm.com", "boc.cn", "icbc.com.cn",
    "china.com", "china.com.cn", "gov.cn", "people.com.cn",
    "xinhuanet.com", "cctv.com", "cntv.cn",
    "hupu.com", "zhibo8.cc", "dongqiudi.com",
    "58.com", "ganji.com", "anjuke.com", "lianjia.com",
    "yunpan.cn", "lanzou.com", "lanzoui.com",
    "xunlei.com", "kuaishou.com", "kwai.com",
    "pptv.com", "mgtv.com", "le.com", "letv.com",
    "yinxiang.com", "evernote.cn", "youdao.com",
    "qunar.com", "elong.com", "ly.com", "fliggy.com",
    "alitrip.com", "tuniu.com", "mafengwo.cn",
    "chinaunicom.com", "10010.com", "189.cn", "10086.cn",
    "mi.com", "xiaomi.com", "miui.com", "miwifi.com",
    "huawei.com", "hicloud.com", "honor.cn", "vmall.com",
    "oppo.com", "vivo.com.cn", "realme.com", "oneplus.com",
    "lenovo.com", "zol.com.cn", "pconline.com.cn",
    "ithome.com", "mydrivers.com", "geekpark.net",
    "gamersky.com", "3dmgame.com", "ali213.net",
    "dytt8.net", "ygdy8.net",
    "panda.tv", "huya.com", "douyu.com", "yy.com",
    "rr.tv", "migu.cn", "migucloud.com", "cmvideo.cn",
    "wo.cn", "wostore.cn", "chinamobile.com",
]

# AI服务规则列表
_AI_RULES = [
    ("DOMAIN", "api.anthropic.com"),
    ("DOMAIN", "console.anthropic.com"),
    ("DOMAIN", "platform.claude.com"),
    ("DOMAIN-SUFFIX", "anthropic.com"),
    ("DOMAIN-SUFFIX", "claude.ai"),
    ("DOMAIN-SUFFIX", "claude.com"),
    ("DOMAIN-SUFFIX", "claudeusercontent.com"),
    ("DOMAIN-SUFFIX", "openai.com"),
    ("DOMAIN-SUFFIX", "chatgpt.com"),
    ("DOMAIN-SUFFIX", "oaistatic.com"),
    ("DOMAIN-SUFFIX", "oaiusercontent.com"),
    ("DOMAIN-SUFFIX", "ai.google.dev"),
    ("DOMAIN-SUFFIX", "gemini.google.com"),
    ("DOMAIN-SUFFIX", "generativeai.google"),
    ("DOMAIN-SUFFIX", "google.com"),
    ("DOMAIN-SUFFIX", "googleapis.com"),
    ("DOMAIN-SUFFIX", "gstatic.com"),
    ("DOMAIN-SUFFIX", "perplexity.ai"),
    ("DOMAIN-SUFFIX", "x.ai")
]

# 预计算的静态规则字符串
_STATIC_IP_RULES = '\n'.join(f"- DOMAIN-SUFFIX,{domain},DIRECT" for domain in _CN_DOMAINS)
_STATIC_AI_RULES = '\n'.join(f"- {rule_type},{domain},🤖 AI专用" for rule_type, domain in _AI_RULES)

# 静态IP节点名称常量
_STATIC_IP_NAME = "🏠 美国/洛杉矶"

# 预编译正则表达式
_SOCKS5_RE = re.compile(r'^(.+?):(.+?)@(.+?):(\d+)$')
_PROXY_KEY_RE = re.compile(r'^([a-zA-Z0-9_-]+):\s*(.*)$')
_PROXIES_HEADER_RE = re.compile(r'^proxies:\s*$')
_PROXY_LIST_ITEM_RE = re.compile(r'^(\s*)-\s*(.*)$')

# 预计算的YAML头部模板
_YAML_HEADER_TEMPLATE = (
    "# 三段式Clash配置文件\n"
    "# 生成时间: {timestamp}\n"
    "# 国内走直连 | 国外走代理 | AI等特殊节点走静态住宅IP\n"
    "\n"
    "allow-lan: true\n"
    "bind-address: '*'\n"
    "mode: rule\n"
    "log-level: info\n"
    "ipv6: false\n"
    "tcp-concurrent: true\n"
    "external-controller: 127.0.0.1:9090\n"
    "geodata-mode: true\n"
    "geo-auto-update: true\n"
    "geo-update-interval: 24\n"
    "\n"
    "profile:\n"
    "  store-selected: true\n"
    "  store-fake-ip: true\n"
    "\n"
    "dns:\n"
    "  enable: true\n"
    "  listen: 127.0.0.1:53\n"
    "  ipv6: false\n"
    "  enhanced-mode: fake-ip\n"
    "  fake-ip-range: 198.18.0.1/16\n"
    "  default-nameserver:\n"
    "  - 223.5.5.5\n"
    "  - 119.29.29.29\n"
    "  nameserver:\n"
    "  - https://doh.pub/dns-query\n"
    "  - https://dns.alidns.com/dns-query\n"
    "  fallback:\n"
    "  - https://1.1.1.1/dns-query\n"
    "  - https://8.8.8.8/dns-query\n"
    "  fallback-filter:\n"
    "    geoip: true\n"
    "    geoip-code: CN\n"
    "    ipcidr:\n"
    "    - 240.0.0.0/4\n"
    "  nameserver-policy:\n"
    "    geosite:cn:\n"
    "    - https://doh.pub/dns-query\n"
    "    - https://dns.alidns.com/dns-query\n"
    "  proxy-server-nameserver:\n"
    "  - https://223.5.5.5/dns-query\n"
    "  - https://doh.pub/dns-query\n"
    "\n"
)

# 全局状态
app_state = {
    'status': 'ready',
    'message': '',
    'output_file': '',
    'logs': [],
    'yaml_content': ''
}


def log(message):
    """添加日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    app_state['logs'].append(log_entry)
    # 防止无界增长
    if len(app_state['logs']) > 200:
        app_state['logs'] = app_state['logs'][-200:]
    print(log_entry)


def parse_socks5_info(ip_line):
    """解析SOCKS5代理信息"""
    ip_line = ip_line.strip()
    if not ip_line:
        return None

    match = _SOCKS5_RE.match(ip_line)
    if match:
        return {
            'server': match.group(3),
            'port': int(match.group(4)),
            'username': match.group(1),
            'password': match.group(2)
        }
    return None


def _escape_proxy_name(name):
    """代理名称YAML转义：含特殊字符时加单引号"""
    if any(c in name for c in _YAML_SPECIAL_CHARS):
        return "'" + name.replace("'", "''") + "'"
    return name


def split_yaml_pairs(text):
    """按顶层逗号分割 key:value 对，处理引号和嵌套"""
    items = []
    current = []
    in_quote = None
    depth = 0
    i = 0
    while i < len(text):
        c = text[i]
        if c in "'\"":
            if in_quote is None:
                in_quote = c
            elif in_quote == c:
                in_quote = None
            current.append(c)
        elif c == '{' or c == '[':
            if in_quote is None:
                depth += 1
            current.append(c)
        elif c == '}' or c == ']':
            if in_quote is None:
                depth -= 1
            current.append(c)
        elif c == ',' and in_quote is None and depth == 0:
            item = ''.join(current).strip()
            if item:
                items.append(item)
            current = []
        else:
            current.append(c)
        i += 1
    item = ''.join(current).strip()
    if item:
        items.append(item)
    return items


def parse_yaml_value(value_str):
    """解析YAML标量值"""
    value_str = value_str.strip()
    if not value_str:
        return ''
    if (value_str.startswith("'") and value_str.endswith("'")) or \
       (value_str.startswith('"') and value_str.endswith('"')):
        return value_str[1:-1]
    lower = value_str.lower()
    if lower == 'true':
        return True
    if lower == 'false':
        return False
    if lower == 'null' or lower == '~':
        return None
    try:
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass
    if value_str.startswith('[') and value_str.endswith(']'):
        inner = value_str[1:-1].strip()
        if not inner:
            return []
        items = split_yaml_pairs(inner)
        return [parse_yaml_value(item) for item in items]
    if value_str.startswith('{') and value_str.endswith('}'):
        inner = value_str[1:-1].strip()
        result = {}
        if not inner:
            return result
        pairs = split_yaml_pairs(inner)
        for pair in pairs:
            if ':' not in pair:
                continue
            idx = pair.index(':')
            k = pair[:idx].strip()
            v = parse_yaml_value(pair[idx + 1:])
            result[k] = v
        return result
    return value_str


def parse_inline_proxy(line):
    """解析单行inline格式 { ... }"""
    line = line.strip()
    if line.startswith('- '):
        line = line[2:].strip()
    if not (line.startswith('{') and line.endswith('}')):
        return None
    inner = line[1:-1].strip()
    proxy = {}
    pairs = split_yaml_pairs(inner)
    for pair in pairs:
        if ':' not in pair:
            continue
        idx = pair.index(':')
        key = pair[:idx].strip()
        value = parse_yaml_value(pair[idx + 1:])
        proxy[key] = value
    return proxy if proxy else None


def parse_yaml_block(lines):
    """递归解析YAML块"""
    result = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        match = _PROXY_KEY_RE.match(stripped)
        if not match:
            i += 1
            continue
        key = match.group(1)
        value = match.group(2).strip()
        current_indent = len(line) - len(line.lstrip())
        if not value:
            nested = []
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                if not nl.strip() or nl.strip().startswith('#'):
                    j += 1
                    continue
                ni = len(nl) - len(nl.lstrip())
                if ni <= current_indent:
                    break
                nested.append(nl)
                j += 1
            if nested:
                if nested[0].strip().startswith('- '):
                    result[key] = []
                    for nl in nested:
                        s = nl.strip()
                        if s.startswith('- '):
                            result[key].append(parse_yaml_value(s[2:]))
                else:
                    result[key] = parse_yaml_block(nested, current_indent)
                i = j
                continue
        result[key] = parse_yaml_value(value)
        i += 1
    return result


def parse_proxy_block(block_lines):
    """通用代理节点解析，支持单行inline和多行标准YAML"""
    if not block_lines:
        return None
    # 尝试单行inline（过滤空行后拼接）
    stripped_lines = [l.strip() for l in block_lines if l.strip()]
    single_line = ' '.join(stripped_lines)
    proxy = parse_inline_proxy(single_line)
    if proxy and 'name' in proxy and 'type' in proxy:
        return validate_proxy(proxy)
    # 多行格式（保留原始缩进）
    proxy = parse_yaml_block(block_lines)
    if proxy and 'name' in proxy and 'type' in proxy:
        return validate_proxy(proxy)
    return None


_SKIP_NAME_KEYWORDS = frozenset(['剩余流量', '距离下次重置', '套餐到期', '有效期'])


def validate_proxy(proxy):
    """验证并标准化代理节点"""
    if not isinstance(proxy, dict):
        return None

    name = proxy.get('name', '')
    proxy_type = proxy.get('type', '')
    server = proxy.get('server', '')
    port = proxy.get('port', 0)

    try:
        port = int(port)
    except (ValueError, TypeError):
        return None

    if not name or not proxy_type or not server or not port:
        return None
    if any(kw in name for kw in _SKIP_NAME_KEYWORDS):
        return None

    proxy['port'] = port
    proxy.setdefault('udp', True)
    return proxy


def _dedup_proxies(proxies):
    """按名称去重，保留首次出现的节点"""
    seen = set()
    result = []
    for proxy in proxies:
        name = proxy.get('name', '')
        if name not in seen:
            seen.add(name)
            result.append(proxy)
        else:
            log(f"[去重] 跳过重复节点: {name}")
    return result


def load_nodes_from_yaml(content):
    """从YAML内容加载代理节点，优先使用标准YAML库"""
    # 优先使用PyYAML（最可靠）
    if _HAS_YAML:
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict) and 'proxies' in data:
                proxies = []
                for proxy in data['proxies']:
                    validated = validate_proxy(proxy)
                    if validated:
                        proxies.append(validated)
                if proxies:
                    proxies = _dedup_proxies(proxies)
                    log(f"[YAML] 标准库解析完成，有效节点: {len(proxies)} 个")
                    return proxies
        except Exception as e:
            log(f"[Info] YAML library parse failed, fallback to compatibility mode: {e}")
    else:
        log("[Info] PyYAML not installed, using compatibility parser")

    # 手写兼容解析器
    proxies = []
    in_proxies = False
    current_block = None
    base_indent = None

    for line in content.split('\n'):
        stripped = line.strip()

        if _PROXIES_HEADER_RE.match(stripped):
            in_proxies = True
            current_block = None
            base_indent = None
            continue

        if in_proxies and stripped and not line.startswith(' ') and not stripped.startswith('#'):
            in_proxies = False
            if current_block is not None:
                proxy = parse_proxy_block(current_block)
                if proxy:
                    proxies.append(proxy)
                current_block = None
            break

        if not in_proxies:
            continue

        match = _PROXY_LIST_ITEM_RE.match(line)
        if match:
            indent = len(match.group(1))
            remaining = match.group(2)

            if base_indent is None:
                base_indent = indent

            if indent <= base_indent:
                # 新代理节点
                if current_block is not None:
                    proxy = parse_proxy_block(current_block)
                    if proxy:
                        proxies.append(proxy)
                current_block = [remaining] if remaining else []
            else:
                # 子列表项（如 alpn 下的 - h2），保留原始行
                if current_block is not None:
                    current_block.append(line)
        elif current_block is not None and line.startswith(' '):
            # 字段行，保留原始缩进
            current_block.append(line)

    if current_block is not None:
        proxy = parse_proxy_block(current_block)
        if proxy:
            proxies.append(proxy)

    proxies = _dedup_proxies(proxies)
    log(f"[兼容] 兼容模式解析完成，有效节点: {len(proxies)} 个")
    return proxies


def load_static_ip(content):
    """加载静态IP信息"""
    lines = [line.strip() for line in content.split('\n') if line.strip()]

    for line in lines:
        parsed = parse_socks5_info(line)
        if parsed:
            return parsed

    return None


def generate_yaml_header():
    """生成YAML头部配置"""
    return _YAML_HEADER_TEMPLATE.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


def yaml_scalar(value):
    """格式化YAML标量值"""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int) or isinstance(value, float):
        return str(value)
    if value is None:
        return 'null'
    s = str(value)
    if any(c in s for c in [':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'", "~", " ", "\n"]) or s == '' or s.lower() in ('true', 'false', 'null', 'yes', 'no', 'on', 'off'):
        return "'" + s.replace("'", "''") + "'"
    return s


def write_yaml_lines(value, indent):
    """递归生成YAML行列表"""
    lines = []
    if isinstance(value, dict):
        for k, v in value.items():
            v_lines = write_yaml_lines(v, indent + 2)
            if len(v_lines) == 1 and not v_lines[0].startswith(' '):
                lines.append(' ' * indent + k + ': ' + v_lines[0])
            else:
                lines.append(' ' * indent + k + ':')
                lines.extend(v_lines)
    elif isinstance(value, list):
        for item in value:
            item_lines = write_yaml_lines(item, indent + 2)
            if len(item_lines) == 1 and not item_lines[0].startswith(' '):
                lines.append(' ' * indent + '- ' + item_lines[0])
            else:
                lines.append(' ' * indent + '-')
                lines.extend(item_lines)
    else:
        lines.append(yaml_scalar(value))
    return lines


def generate_proxies_section(proxies, static_ip_info, static_ip_name):
    """生成proxies部分，保留所有原始字段"""
    lines = ["proxies:"]

    for proxy in proxies:
        if proxy.get('name') == static_ip_name:
            continue
        lines.append("- name: " + yaml_scalar(proxy.get('name', '')))
        for key, value in proxy.items():
            if key == 'name':
                continue
            val_lines = write_yaml_lines(value, 4)
            if len(val_lines) == 1 and not val_lines[0].startswith(' '):
                lines.append("  " + key + ": " + val_lines[0])
            else:
                lines.append("  " + key + ":")
                lines.extend(val_lines)

    # 添加静态住宅IP节点
    lines.append("- name: " + yaml_scalar(static_ip_name))
    lines.append("  type: socks5")
    lines.append("  server: " + yaml_scalar(static_ip_info['server']))
    lines.append("  port: " + yaml_scalar(static_ip_info['port']))
    lines.append("  username: " + yaml_scalar(static_ip_info['username']))
    lines.append("  password: " + yaml_scalar(static_ip_info['password']))
    lines.append("  udp: true")
    lines.append("  dialer-proxy: " + yaml_scalar('✈️ 前置中转'))

    lines.append("")
    return '\n'.join(lines)


def generate_proxy_groups(proxy_names, static_ip_name=_STATIC_IP_NAME, transit_proxies=None):
    """生成proxy-groups部分"""
    if transit_proxies is None:
        transit_proxies = proxy_names

    lines = ["proxy-groups:"]

    # 静态IP节点不能放入url-test组（会因dialer-proxy产生循环依赖）
    url_test_proxies = [n for n in transit_proxies if n != static_ip_name]

    # 前置中转-自动
    lines.append("- name: '✈️ 前置中转-自动'")
    lines.append("  type: url-test")
    lines.append("  url: http://www.gstatic.com/generate_204")
    lines.append("  interval: 300")
    lines.append("  tolerance: 50")
    lines.append("  proxies:")
    for name in url_test_proxies:
        lines.append(f"  - {_escape_proxy_name(name)}")

    # 前置中转
    lines.append("- name: '✈️ 前置中转'")
    lines.append("  type: select")
    lines.append("  proxies:")
    lines.append("  - '✈️ 前置中转-自动'")
    for name in transit_proxies:
        lines.append(f"  - {_escape_proxy_name(name)}")

    # 国外网站
    lines.append("- name: '🌍 国外网站'")
    lines.append("  type: select")
    lines.append("  proxies:")
    lines.append("  - '✈️ 前置中转'")
    lines.append("  - DIRECT")

    # 静态住宅IP
    lines.append("- name: '🏠 静态住宅IP'")
    lines.append("  type: select")
    lines.append("  proxies:")
    static_name = proxy_names[-1] if proxy_names else static_ip_name
    lines.append(f"  - {_escape_proxy_name(static_name)}")
    lines.append("  - '✈️ 前置中转'")

    # AI专用
    lines.append("- name: '🤖 AI专用'")
    lines.append("  type: select")
    lines.append("  proxies:")
    lines.append("  - '🏠 静态住宅IP'")
    lines.append("  - '✈️ 前置中转'")

    lines.append("")
    return '\n'.join(lines)


def generate_rules():
    """生成rules部分"""
    return (
        "rules:\n"
        "- IP-CIDR,127.0.0.0/8,DIRECT,no-resolve\n"
        "- IP-CIDR,172.16.0.0/12,DIRECT,no-resolve\n"
        "- IP-CIDR,192.168.0.0/16,DIRECT,no-resolve\n"
        "- IP-CIDR,10.0.0.0/8,DIRECT,no-resolve\n"
        "- IP-CIDR,100.64.0.0/10,DIRECT,no-resolve\n"
        "- IP-CIDR,224.0.0.0/4,DIRECT,no-resolve\n"
        "- IP-CIDR,fe80::/10,DIRECT,no-resolve\n"
        "- IP-CIDR,fc00::/7,DIRECT,no-resolve\n"
        + _STATIC_IP_RULES + "\n"
        "- GEOSITE,CN,DIRECT\n"
        "- GEOIP,CN,DIRECT,no-resolve\n"
        + _STATIC_AI_RULES + "\n"
        "- MATCH,🌍 国外网站"
    )


def generate_three_stage_yaml(node_content, ip_content, output_file, include_static_in_transit=True):
    """生成三段式配置文件"""

    # 1. 加载节点
    log("[步骤1] 加载节点配置文件...")
    proxies = load_nodes_from_yaml(node_content)
    if not proxies:
        log("[错误] 未能加载任何有效节点")
        return False
    log(f"        找到 {len(proxies)} 个有效代理节点")

    # 2. 加载静态IP
    log("[步骤2] 加载静态住宅IP信息...")
    static_ip = load_static_ip(ip_content)
    if not static_ip:
        log("[错误] 未能加载静态IP信息")
        return False
    log(f"        服务器: {static_ip['server']}")
    log(f"        端口: {static_ip['port']}")

    # 3. 生成配置内容
    log("[步骤3] 生成三段式配置...")
    static_ip_name = _STATIC_IP_NAME

    # 收集代理名称
    proxy_names = [p['name'] for p in proxies]
    proxy_names.append(static_ip_name)

    # 根据 include_static_in_transit 决定如何构建前置中转节点列表
    transit_proxies = proxy_names if include_static_in_transit else proxy_names[:-1]

    # 生成完整配置
    yaml_content = '\n'.join([
        generate_yaml_header(),
        generate_proxies_section(proxies, static_ip, static_ip_name),
        generate_proxy_groups(proxy_names, static_ip_name, transit_proxies),
        generate_rules()
    ])

    # 保存配置
    log("[步骤4] 保存配置文件...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        log(f"[成功] 配置已保存到: {output_file}")
        app_state['output_file'] = output_file
        app_state['yaml_content'] = yaml_content
        return True
    except Exception as e:
        log(f"[错误] 保存配置文件失败: {e}")
        return False


# ============== Web服务器部分 ==============

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/' or path == '/index.html':
            self.send_index()
        elif path == '/style.css':
            self.send_css()
        elif path == '/script.js':
            self.send_js()
        elif path == '/api/status':
            self.send_json({
                'status': app_state['status'],
                'message': app_state['message'],
                'output_file': app_state['output_file'],
                'logs': app_state['logs'][-50:]
            })
        elif path == '/api/download':
            self.send_download()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/generate':
            self.handle_generate()
        elif self.path == '/api/upload':
            self.handle_upload()
        else:
            self.send_error(404)

    def _send_text(self, content, content_type):
        """发送文本响应"""
        self.send_response(200)
        self.send_header('Content-Type', f'{content_type}; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def send_index(self):
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clash三段式配置生成器</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Clash三段式配置生成器</h1>
            <p class="subtitle">国内直连 | 国外代理 | AI专用静态IP</p>
        </header>

        <main>
            <div class="card">
                <h2>📁 文件上传</h2>
                <div class="upload-area" id="uploadArea">
                    <div class="upload-content">
                        <span class="icon">📂</span>
                        <p>拖拽文件到此处，或点击选择文件</p>
                        <span class="hint">支持：节点信息.yaml、静态住宅IP.txt</span>
                    </div>
                    <input type="file" id="fileInput" accept=".yaml,.yml,.txt" multiple>
                </div>
                <div class="file-list" id="fileList"></div>
            </div>

            <div class="card">
                <h2>⚙️ 生成配置</h2>
                <div class="form-group">
                    <label for="outputName">输出文件名：</label>
                    <input type="text" id="outputName" value="三段式节点信息.yaml" placeholder="三段式节点信息.yaml">
                </div>
                <button class="btn btn-primary" id="generateBtn" disabled>
                    <span class="btn-text">🚀 开始生成配置</span>
                    <span class="btn-loading" hidden>⏳ 生成中...</span>
                </button>
            </div>

            <div class="card" id="statusCard" hidden>
                <h2>📊 生成状态</h2>
                <div class="status-content">
                    <div class="status-indicator" id="statusIndicator">
                        <span class="status-dot"></span>
                        <span class="status-text">准备就绪</span>
                    </div>
                    <div class="progress-bar" hidden id="progressBar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </div>

            <div class="card" id="logCard">
                <h2>📝 运行日志</h2>
                <div class="log-container" id="logContainer">
                    <div class="log-placeholder">等待生成...</div>
                </div>
                <div class="log-actions">
                    <button class="btn btn-sm btn-secondary" id="clearLogsBtn">清空日志</button>
                    <button class="btn btn-sm btn-secondary" id="downloadLogsBtn">下载日志</button>
                </div>
            </div>

            <div class="card" id="previewCard" hidden>
                <h2>👁️ 配置预览</h2>
                <div class="preview-actions">
                    <button class="btn btn-sm btn-primary" id="downloadBtn">📥 下载配置</button>
                </div>
                <div class="preview-container">
                    <pre id="previewContent"></pre>
                </div>
            </div>
        </main>

        <footer>
            <p>Clash三段式配置生成器 | 版本 1.0</p>
        </footer>
    </div>

    <script src="script.js"></script>
</body>
</html>'''
        self._send_text(html, 'text/html')

    def send_css(self):
        css = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 900px;
    margin: 0 auto;
}

header {
    text-align: center;
    padding: 40px 0;
    color: white;
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.subtitle {
    font-size: 1.1em;
    opacity: 0.9;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-2px);
}

.card h2 {
    color: #333;
    font-size: 1.3em;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f0f0;
}

.upload-area {
    border: 3px dashed #d1d5db;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #fafafa;
    position: relative;
    overflow: hidden;
}

#fileInput {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    z-index: 10;
}

.upload-area:hover {
    border-color: #667eea;
    background: #f0f4ff;
}

.upload-area.dragover {
    border-color: #667eea;
    background: #e0e7ff;
    transform: scale(1.02);
}

.upload-content .icon {
    font-size: 3em;
    margin-bottom: 12px;
    display: block;
}

.upload-content p {
    color: #4b5563;
    font-size: 1.1em;
    margin-bottom: 8px;
}

.upload-content .hint {
    color: #9ca3af;
    font-size: 0.9em;
}

.file-list {
    margin-top: 20px;
}

.file-placeholder {
    color: #9ca3af;
    text-align: center;
    padding: 16px;
    font-size: 0.95em;
}

.file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #f9fafb;
    border-radius: 8px;
    margin-bottom: 10px;
    border: 1px solid #e5e7eb;
}

.file-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.file-icon {
    font-size: 1.5em;
}

.file-details {
    display: flex;
    flex-direction: column;
}

.file-name {
    font-weight: 500;
    color: #111827;
}

.file-size {
    font-size: 0.85em;
    color: #6b7280;
}

.file-actions {
    display: flex;
    gap: 8px;
}

.btn-icon {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 6px;
    transition: background 0.2s;
    font-size: 1.1em;
}

.btn-icon:hover {
    background: #e5e7eb;
}

.btn-icon.remove:hover {
    background: #fee2e2;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #374151;
    font-weight: 500;
}

.form-group input[type="text"] {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 1em;
    transition: border-color 0.3s;
}

.form-group input[type="text"]:focus {
    outline: none;
    border-color: #667eea;
}


.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 1em;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    width: 100%;
    padding: 16px;
    font-size: 1.1em;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
    background: #f3f4f6;
    color: #374151;
}

.btn-secondary:hover {
    background: #e5e7eb;
}

.btn-sm {
    padding: 8px 16px;
    font-size: 0.9em;
}

.status-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 12px;
}

.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.status-text {
    color: #374151;
    font-weight: 500;
}

.progress-bar {
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    width: 0%;
    transition: width 0.3s ease;
}

.log-container {
    background: #1f2937;
    border-radius: 8px;
    padding: 16px;
    height: 300px;
    overflow-y: auto;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

.log-placeholder {
    color: #6b7280;
    text-align: center;
    padding: 40px 0;
}

.log-entry {
    color: #d1d5db;
    padding: 2px 0;
    border-bottom: 1px solid #374151;
}

.log-entry.success {
    color: #10b981;
}

.log-entry.error {
    color: #ef4444;
}

.log-actions {
    display: flex;
    gap: 10px;
    margin-top: 12px;
}

.preview-actions {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
}

.preview-container {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    max-height: 500px;
    overflow: auto;
}

.preview-container pre {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.85em;
    line-height: 1.6;
    color: #374151;
    white-space: pre-wrap;
    word-wrap: break-word;
}

footer {
    text-align: center;
    padding: 20px;
    color: rgba(255,255,255,0.8);
}

.hidden {
    display: none !important;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.card {
    animation: fadeIn 0.4s ease-out;
}

@media (max-width: 768px) {
    body {
        padding: 10px;
    }

    header h1 {
        font-size: 1.8em;
    }

    .card {
        padding: 20px;
    }

    .upload-area {
        padding: 30px 20px;
    }

    .file-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .log-container {
        height: 200px;
    }
}
'''
        self._send_text(css, 'text/css')

    def send_js(self):
        js = r'''// 全局状态
let nodeFile = null;
let staticIpFile = null;

// DOM元素（延迟获取，确保DOM已就绪）
function getEl(id) { return document.getElementById(id); }

let uploadArea, fileInput, fileList, generateBtn, outputName;
let statusCard, statusText, statusDot, logContainer, previewCard, previewContent;

function initElements() {
    uploadArea = getEl('uploadArea');
    fileInput = getEl('fileInput');
    fileList = getEl('fileList');
    generateBtn = getEl('generateBtn');
    outputName = getEl('outputName');
    statusCard = getEl('statusCard');
    statusText = document.querySelector('.status-text');
    statusDot = document.querySelector('.status-dot');
    logContainer = getEl('logContainer');
    previewCard = getEl('previewCard');
    previewContent = getEl('previewContent');
}

// 安全初始化（兼容DOMContentLoaded已触发的情况）
function init() {
    initElements();
    if (!fileInput) {
        console.error('[init] fileInput not found, retrying in 100ms');
        setTimeout(init, 100);
        return;
    }
    setupEventListeners();
    updateFileList();
    updateGenerateButton();
    log('页面初始化完成，等待上传文件...');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// 事件监听
function setupEventListeners() {
    if (!uploadArea || !fileInput) return;

    // 文件上传（fileInput 已透明覆盖在 uploadArea 上，直接点击即可触发）
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // 生成按钮
    if (generateBtn) {
        generateBtn.addEventListener('click', handleGenerate);
    }

    // 清空日志
    const clearLogsBtn = getEl('clearLogsBtn');
    if (clearLogsBtn && logContainer) {
        clearLogsBtn.addEventListener('click', () => {
            logContainer.innerHTML = '<div class="log-placeholder">等待生成...</div>';
        });
    }

    // 下载日志
    const downloadLogsBtn = getEl('downloadLogsBtn');
    if (downloadLogsBtn) {
        downloadLogsBtn.addEventListener('click', downloadLogs);
    }

    // 下载配置
    const downloadBtn = getEl('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadConfig);
    }
}

// 拖拽处理
function handleDragOver(e) {
    e.preventDefault();
    if (uploadArea) uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    if (uploadArea) uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    if (uploadArea) uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    processFiles(files);
    // 清空 input 值，允许再次选择同一文件
    e.target.value = '';
}

// 获取文件扩展名（更健壮）
function getFileExtension(filename) {
    const lastDot = filename.lastIndexOf('.');
    if (lastDot === -1 || lastDot === 0 || lastDot === filename.length - 1) {
        return '';
    }
    return filename.slice(lastDot).toLowerCase();
}

// 处理文件
function processFiles(files) {
    if (!files || files.length === 0) {
        log('[提示] 未选择任何文件');
        return;
    }

    log(`开始处理 ${files.length} 个文件...`);

    files.forEach(file => {
        const ext = getFileExtension(file.name);
        log(`检测到文件: ${file.name} (扩展名: ${ext || '无'})`);

        if (ext !== '.yaml' && ext !== '.yml' && ext !== '.txt') {
            log(`[提示] 跳过不支持的文件: ${file.name}（仅支持 .yaml/.yml/.txt）`);
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const content = e.target.result;
                if (ext === '.yaml' || ext === '.yml') {
                    nodeFile = { name: file.name, content };
                    log(`已加载节点文件: ${file.name}`);
                } else if (ext === '.txt') {
                    staticIpFile = { name: file.name, content };
                    log(`已加载静态IP文件: ${file.name}`);
                }
                updateFileList();
                updateGenerateButton();
            } catch (err) {
                log(`[错误] 处理文件内容时出错: ${err.message}`);
                console.error(err);
            }
        };
        reader.onerror = () => {
            log(`[错误] 读取文件失败: ${file.name}`);
        };
        reader.readAsText(file);
    });
}

// 更新文件列表
function updateFileList() {
    if (!fileList) {
        console.error('[updateFileList] fileList element not found');
        return;
    }

    fileList.innerHTML = '';

    if (!nodeFile && !staticIpFile) {
        fileList.innerHTML = '<div class="file-placeholder">尚未上传文件</div>';
        return;
    }

    if (nodeFile) {
        addFileItem(nodeFile.name, '📄', 'node');
    }

    if (staticIpFile) {
        addFileItem(staticIpFile.name, '📋', 'static');
    }
}

function addFileItem(name, icon, type) {
    if (!fileList) return;

    const item = document.createElement('div');
    item.className = 'file-item';

    const fileInfo = document.createElement('div');
    fileInfo.className = 'file-info';

    const fileIcon = document.createElement('span');
    fileIcon.className = 'file-icon';
    fileIcon.textContent = icon;

    const fileDetails = document.createElement('div');
    fileDetails.className = 'file-details';

    const fileName = document.createElement('span');
    fileName.className = 'file-name';
    fileName.textContent = name;

    fileDetails.appendChild(fileName);
    fileInfo.appendChild(fileIcon);
    fileInfo.appendChild(fileDetails);

    const fileActions = document.createElement('div');
    fileActions.className = 'file-actions';

    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn-icon remove';
    removeBtn.title = '删除';
    removeBtn.textContent = '❌';
    removeBtn.onclick = () => removeFile(type);

    fileActions.appendChild(removeBtn);
    item.appendChild(fileInfo);
    item.appendChild(fileActions);
    fileList.appendChild(item);
}

function removeFile(type) {
    if (type === 'node') {
        nodeFile = null;
    } else if (type === 'static') {
        staticIpFile = null;
    }
    updateFileList();
    updateGenerateButton();
}

function updateGenerateButton() {
    if (!generateBtn) return;
    if (nodeFile && staticIpFile) {
        generateBtn.disabled = false;
    } else {
        generateBtn.disabled = true;
    }
}

function log(message) {
    const container = logContainer || getEl('logContainer');
    if (!container) {
        console.log('[log]', message);
        return;
    }

    if (container.querySelector('.log-placeholder')) {
        container.innerHTML = '';
    }

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    if (message.includes('[错误]')) {
        entry.classList.add('error');
    } else if (message.includes('[成功]')) {
        entry.classList.add('success');
    }

    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

async function handleGenerate() {
    if (!nodeFile || !staticIpFile) return;

    const outputFile = outputName.value || '三段式节点信息.yaml';

    generateBtn.disabled = true;
    const btnText = document.querySelector('.btn-text');
    const btnLoading = document.querySelector('.btn-loading');
    if (btnText) btnText.hidden = true;
    if (btnLoading) btnLoading.hidden = false;

    statusCard.hidden = false;
    if (statusText) statusText.textContent = '生成中...';
    if (statusDot) statusDot.style.background = '#f59e0b';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nodeContent: nodeFile.content,
                ipContent: staticIpFile.content,
                outputFile: outputFile
            })
        });

        const result = await response.json();

        if (result.success) {
            if (statusText) statusText.textContent = '生成成功！';
            if (statusDot) statusDot.style.background = '#10b981';

            log(`[成功] 配置已生成: ${result.outputFile}`);

            previewCard.hidden = false;
            if (previewContent) previewContent.textContent = result.yamlContent;
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        if (statusText) statusText.textContent = '生成失败';
        if (statusDot) statusDot.style.background = '#ef4444';
        log(`[错误] ${error.message}`);
    } finally {
        generateBtn.disabled = false;
        if (btnText) btnText.hidden = false;
        if (btnLoading) btnLoading.hidden = true;
    }
}

function downloadLogs() {
    const container = logContainer || getEl('logContainer');
    if (!container) return;
    const logs = Array.from(container.querySelectorAll('.log-entry')).map(e => e.textContent).join('\n');

    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `clash-config-logs-${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

function downloadConfig() {
    const pContent = previewContent || getEl('previewContent');
    const content = pContent ? pContent.textContent : '';
    const outName = outputName || getEl('outputName');
    const outputFile = outName ? outName.value : '三段式节点信息.yaml';

    const blob = new Blob([content], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = outputFile;
    a.click();
    URL.revokeObjectURL(url);
}
'''
        self._send_text(js, 'application/javascript')

    def send_json(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def send_download(self):
        """发送配置文件下载"""
        if not app_state.get('yaml_content'):
            self.send_error(404, '配置未生成')
            return

        content = app_state['yaml_content']
        filename = app_state.get('output_file', '三段式节点信息.yaml')

        content_bytes = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/yaml; charset=utf-8')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Content-Length', len(content_bytes))
        self.end_headers()
        self.wfile.write(content_bytes)

    def handle_generate(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_json({'success': False, 'message': '请求体为空'})
            return

        try:
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            node_content = data.get('nodeContent', '')
            ip_content = data.get('ipContent', '')
            output_file = data.get('outputFile', '三段式节点信息.yaml')
            # 重置状态
            app_state['logs'] = []
            app_state['status'] = 'processing'
            app_state['output_file'] = ''
            app_state['yaml_content'] = ''

            # 生成配置（静态IP不参与前置中转url-test组）
            success = generate_three_stage_yaml(
                node_content,
                ip_content,
                output_file,
                False
            )

            if success:
                app_state['status'] = 'done'
                self.send_json({
                    'success': True,
                    'message': '配置生成成功',
                    'outputFile': output_file,
                    'yamlContent': app_state.get('yaml_content', '')
                })
            else:
                app_state['status'] = 'error'
                self.send_json({
                    'success': False,
                    'message': '配置生成失败，请检查日志'
                })

        except Exception as e:
            app_state['status'] = 'error'
            self.send_json({
                'success': False,
                'message': f'处理请求时出错: {str(e)}'
            })

    def handle_upload(self):
        self.send_json({'success': True, 'message': '文件上传通过前端处理'})


def open_browser(port):
    def delayed_open():
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{port}')

    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()


def main():
    port = 8888

    # 允许通过命令行指定端口
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"无效的端口号: {sys.argv[1]}，使用默认端口 {port}")

    server = ThreadedHTTPServer(('localhost', port), RequestHandler)

    print("=" * 60)
    print("  Clash三段式配置生成器 - Web版本")
    print("=" * 60)
    print(f"\n  访问地址: http://localhost:{port}")
    print("  正在启动服务器...")
    print("\n  提示：")
    print("  - 系统会自动打开浏览器")
    print("  - 如未自动打开，请手动访问上述地址")
    print("  - 按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")

    # 打开浏览器
    open_browser(port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  服务器已停止")
        print("  感谢使用 Clash三段式配置生成器！\n")
        sys.exit(0)


if __name__ == '__main__':
    main()
