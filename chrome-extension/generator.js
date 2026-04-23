// ==================== 常量定义 ====================

const YAML_SPECIAL_CHARS = new Set([':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'", '~']);

const CN_DOMAINS = [
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
];

const AI_RULES = [
    ["DOMAIN", "api.anthropic.com"],
    ["DOMAIN", "console.anthropic.com"],
    ["DOMAIN", "platform.claude.com"],
    ["DOMAIN-SUFFIX", "anthropic.com"],
    ["DOMAIN-SUFFIX", "claude.ai"],
    ["DOMAIN-SUFFIX", "claude.com"],
    ["DOMAIN-SUFFIX", "claudeusercontent.com"],
    ["DOMAIN-SUFFIX", "openai.com"],
    ["DOMAIN-SUFFIX", "chatgpt.com"],
    ["DOMAIN-SUFFIX", "oaistatic.com"],
    ["DOMAIN-SUFFIX", "oaiusercontent.com"],
    ["DOMAIN-SUFFIX", "ai.google.dev"],
    ["DOMAIN-SUFFIX", "gemini.google.com"],
    ["DOMAIN-SUFFIX", "generativeai.google"],
    ["DOMAIN-SUFFIX", "google.com"],
    ["DOMAIN-SUFFIX", "googleapis.com"],
    ["DOMAIN-SUFFIX", "gstatic.com"],
    ["DOMAIN-SUFFIX", "perplexity.ai"],
    ["DOMAIN-SUFFIX", "x.ai"]
];

const STATIC_IP_NAME = "🏠 美国/洛杉矶";

const SKIP_NAME_KEYWORDS = new Set(['剩余流量', '距离下次重置', '套餐到期', '有效期']);

const STATIC_IP_RULES = CN_DOMAINS.map(domain => `- DOMAIN-SUFFIX,${domain},DIRECT`).join('\n');
const STATIC_AI_RULES = AI_RULES.map(([ruleType, domain]) => `- ${ruleType},${domain},🤖 AI专用`).join('\n');

const YAML_HEADER_TEMPLATE = (
    "# 三段式Clash配置文件\n" +
    "# 生成时间: {timestamp}\n" +
    "# 国内走直连 | 国外走代理 | AI等特殊节点走静态住宅IP\n" +
    "\n" +
    "allow-lan: true\n" +
    "bind-address: '*'\n" +
    "mode: rule\n" +
    "log-level: info\n" +
    "ipv6: false\n" +
    "tcp-concurrent: true\n" +
    "external-controller: 127.0.0.1:9090\n" +
    "geodata-mode: true\n" +
    "geo-auto-update: true\n" +
    "geo-update-interval: 24\n" +
    "\n" +
    "profile:\n" +
    "  store-selected: true\n" +
    "  store-fake-ip: true\n" +
    "\n" +
    "dns:\n" +
    "  enable: true\n" +
    "  listen: 127.0.0.1:53\n" +
    "  ipv6: false\n" +
    "  enhanced-mode: fake-ip\n" +
    "  fake-ip-range: 198.18.0.1/16\n" +
    "  default-nameserver:\n" +
    "  - 223.5.5.5\n" +
    "  - 119.29.29.29\n" +
    "  nameserver:\n" +
    "  - https://doh.pub/dns-query\n" +
    "  - https://dns.alidns.com/dns-query\n" +
    "  fallback:\n" +
    "  - https://1.1.1.1/dns-query\n" +
    "  - https://8.8.8.8/dns-query\n" +
    "  fallback-filter:\n" +
    "    geoip: true\n" +
    "    geoip-code: CN\n" +
    "    ipcidr:\n" +
    "    - 240.0.0.0/4\n" +
    "  nameserver-policy:\n" +
    "    geosite:cn:\n" +
    "    - https://doh.pub/dns-query\n" +
    "    - https://dns.alidns.com/dns-query\n" +
    "  proxy-server-nameserver:\n" +
    "  - https://223.5.5.5/dns-query\n" +
    "  - https://doh.pub/dns-query\n"
);


// ==================== 辅助函数 ====================

function parseSocks5Info(ipLine) {
    ipLine = ipLine.trim();
    if (!ipLine) return null;
    const pattern = /^(.+?):(.+?)@(.+?):(\d+)$/;
    const match = ipLine.match(pattern);
    if (match) {
        return {
            server: match[3],
            port: parseInt(match[4], 10),
            username: match[1],
            password: match[2]
        };
    }
    return null;
}

function escapeProxyName(name) {
    const chars = Array.from(YAML_SPECIAL_CHARS);
    if (chars.some(c => name.includes(c))) {
        return "'" + name.replace(/'/g, "''") + "'";
    }
    return name;
}

function yamlScalar(value) {
    if (typeof value === 'boolean') {
        return value ? 'true' : 'false';
    }
    if (typeof value === 'number') {
        return String(value);
    }
    if (value === null || value === undefined) {
        return 'null';
    }
    const s = String(value);
    const specialChars = [':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'", "~", " ", "\n"];
    if (specialChars.some(c => s.includes(c)) || s === '' || ['true', 'false', 'null', 'yes', 'no', 'on', 'off'].includes(s.toLowerCase())) {
        return "'" + s.replace(/'/g, "''") + "'";
    }
    return s;
}

function splitYamlPairs(text) {
    const items = [];
    const current = [];
    let inQuote = null;
    let depth = 0;
    let i = 0;
    while (i < text.length) {
        const c = text[i];
        if (c === "'" || c === '"') {
            if (inQuote === null) {
                inQuote = c;
            } else if (inQuote === c) {
                inQuote = null;
            }
            current.push(c);
        } else if (c === '{' || c === '[') {
            if (inQuote === null) {
                depth += 1;
            }
            current.push(c);
        } else if (c === '}' || c === ']') {
            if (inQuote === null) {
                depth -= 1;
            }
            current.push(c);
        } else if (c === ',' && inQuote === null && depth === 0) {
            const item = current.join('').trim();
            if (item) {
                items.push(item);
            }
            current.length = 0;
        } else {
            current.push(c);
        }
        i++;
    }
    const item = current.join('').trim();
    if (item) {
        items.push(item);
    }
    return items;
}

function parseYamlValue(valueStr) {
    valueStr = valueStr.trim();
    if (!valueStr) {
        return '';
    }
    if ((valueStr.startsWith("'") && valueStr.endsWith("'")) ||
        (valueStr.startsWith('"') && valueStr.endsWith('"'))) {
        return valueStr.slice(1, -1);
    }
    const lower = valueStr.toLowerCase();
    if (lower === 'true') {
        return true;
    }
    if (lower === 'false') {
        return false;
    }
    if (lower === 'null' || lower === '~') {
        return null;
    }
    if (/^\d+$/.test(valueStr)) {
        return parseInt(valueStr, 10);
    }
    if (/^\d+\.\d+$/.test(valueStr)) {
        return parseFloat(valueStr);
    }
    if (valueStr.startsWith('[') && valueStr.endsWith(']')) {
        const inner = valueStr.slice(1, -1).trim();
        if (!inner) {
            return [];
        }
        const items = splitYamlPairs(inner);
        return items.map(item => parseYamlValue(item));
    }
    if (valueStr.startsWith('{') && valueStr.endsWith('}')) {
        const inner = valueStr.slice(1, -1).trim();
        const result = {};
        if (!inner) {
            return result;
        }
        const pairs = splitYamlPairs(inner);
        for (const pair of pairs) {
            const idx = pair.indexOf(':');
            if (idx === -1) {
                continue;
            }
            const k = pair.slice(0, idx).trim();
            const v = parseYamlValue(pair.slice(idx + 1));
            result[k] = v;
        }
        return result;
    }
    return valueStr;
}

function parseInlineProxy(line) {
    line = line.trim();
    if (line.startsWith('- ')) {
        line = line.slice(2).trim();
    }
    if (!(line.startsWith('{') && line.endsWith('}'))) {
        return null;
    }
    const inner = line.slice(1, -1).trim();
    const proxy = {};
    const pairs = splitYamlPairs(inner);
    for (const pair of pairs) {
        const idx = pair.indexOf(':');
        if (idx === -1) {
            continue;
        }
        const key = pair.slice(0, idx).trim();
        const value = parseYamlValue(pair.slice(idx + 1));
        proxy[key] = value;
    }
    return Object.keys(proxy).length > 0 ? proxy : null;
}

function parseYamlBlock(lines) {
    const result = {};
    let i = 0;
    while (i < lines.length) {
        const line = lines[i];
        const stripped = line.trim();
        if (!stripped || stripped.startsWith('#')) {
            i++;
            continue;
        }
        const proxyKeyRe = /^([a-zA-Z0-9_-]+):\s*(.*)$/;
        const match = stripped.match(proxyKeyRe);
        if (!match) {
            i++;
            continue;
        }
        const key = match[1];
        const value = match[2].trim();
        const currentIndent = line.length - line.trimStart().length;
        if (!value) {
            const nested = [];
            let j = i + 1;
            while (j < lines.length) {
                const nl = lines[j];
                if (!nl.trim() || nl.trim().startsWith('#')) {
                    j++;
                    continue;
                }
                const ni = nl.length - nl.trimStart().length;
                if (ni <= currentIndent) {
                    break;
                }
                nested.push(nl);
                j++;
            }
            if (nested.length > 0) {
                if (nested[0].trim().startsWith('- ')) {
                    result[key] = [];
                    for (const nl of nested) {
                        const s = nl.trim();
                        if (s.startsWith('- ')) {
                            result[key].push(parseYamlValue(s.slice(2)));
                        }
                    }
                } else {
                    result[key] = parseYamlBlock(nested);
                }
                i = j;
                continue;
            }
        }
        result[key] = parseYamlValue(value);
        i++;
    }
    return result;
}

function parseProxyBlock(blockLines) {
    if (!blockLines || blockLines.length === 0) {
        return null;
    }
    const strippedLines = blockLines.filter(l => l.trim()).map(l => l.trim());
    const singleLine = strippedLines.join(' ');
    let proxy = parseInlineProxy(singleLine);
    if (proxy && proxy.name && proxy.type) {
        return validateProxy(proxy);
    }
    proxy = parseYamlBlock(blockLines);
    if (proxy && proxy.name && proxy.type) {
        return validateProxy(proxy);
    }
    return null;
}

function validateProxy(proxy) {
    if (!proxy || typeof proxy !== 'object') {
        return null;
    }
    const name = proxy.name || '';
    const proxyType = proxy.type || '';
    const server = proxy.server || '';
    let port = proxy.port || 0;
    port = parseInt(port, 10);
    if (isNaN(port)) {
        return null;
    }
    if (!name || !proxyType || !server || !port) {
        return null;
    }
    const skipKeywords = Array.from(SKIP_NAME_KEYWORDS);
    if (skipKeywords.some(kw => name.includes(kw))) {
        return null;
    }
    proxy.port = port;
    if (proxy.udp === undefined) {
        proxy.udp = true;
    }
    return proxy;
}

function dedupProxies(proxies, logs) {
    const seen = new Set();
    const result = [];
    for (const proxy of proxies) {
        const name = proxy.name || '';
        if (!seen.has(name)) {
            seen.add(name);
            result.push(proxy);
        } else {
            logs.push(`[去重] 跳过重复节点: ${name}`);
        }
    }
    return result;
}

function loadNodesFromYaml(content, logs) {
    const proxies = [];
    let inProxies = false;
    let currentBlock = null;
    let baseIndent = null;
    let lineNum = 0;

    logs.push(`[调试] 开始解析节点内容，内容长度: ${content.length} 字符`);

    for (const line of content.split(/\r?\n/)) {
        lineNum++;
        const stripped = line.trim();

        // 放宽匹配：只要行首是 proxies: 即可（允许后面跟注释）
        if (/^proxies:/.test(stripped)) {
            inProxies = true;
            currentBlock = null;
            baseIndent = null;
            logs.push(`[调试] 第 ${lineNum} 行找到 proxies: 头部`);
            continue;
        }

        // 退出 proxies 块：非空行、非注释、非列表项，且不以空白字符开头
        if (inProxies && stripped && !/^\s/.test(line) && !stripped.startsWith('#') && !stripped.startsWith('-')) {
            inProxies = false;
            if (currentBlock !== null) {
                const proxy = parseProxyBlock(currentBlock);
                if (proxy) {
                    proxies.push(proxy);
                } else {
                    logs.push(`[调试] 退出前最后一个 block 解析失败`);
                }
                currentBlock = null;
            }
            logs.push(`[调试] 第 ${lineNum} 行退出 proxies 块，遇到新键: ${stripped.slice(0, 40)}`);
            break;
        }

        if (!inProxies) {
            continue;
        }

        const match = line.match(/^(\s*)-\s*(.*)$/);
        if (match) {
            const indent = match[1].length;
            const remaining = match[2];

            if (baseIndent === null) {
                baseIndent = indent;
                logs.push(`[调试] 第一个列表项缩进 ${indent} 个空白字符`);
            }

            if (indent <= baseIndent) {
                // 新代理节点
                if (currentBlock !== null) {
                    const proxy = parseProxyBlock(currentBlock);
                    if (proxy) {
                        proxies.push(proxy);
                    } else if (currentBlock.some(l => l.trim())) {
                        logs.push(`[调试] block 解析失败，首行: ${currentBlock[0].trim().slice(0, 60)}`);
                    }
                }
                currentBlock = remaining ? [remaining] : [];
            } else {
                // 子列表项（如 alpn 下的 - h2），保留原始行
                if (currentBlock !== null) {
                    currentBlock.push(line);
                }
            }
        } else if (currentBlock !== null && /^\s/.test(line)) {
            // 字段行：支持空格或 Tab 缩进
            currentBlock.push(line);
        }
    }

    if (currentBlock !== null) {
        const proxy = parseProxyBlock(currentBlock);
        if (proxy) {
            proxies.push(proxy);
        } else if (currentBlock.some(l => l.trim())) {
            logs.push(`[调试] 最后一个 block 解析失败，首行: ${currentBlock[0].trim().slice(0, 60)}`);
        }
    }

    if (proxies.length === 0) {
        logs.push(`[调试] 未找到 proxies: 头部或未能解析任何节点，请检查文件是否为标准 Clash YAML 格式`);
    }

    const result = dedupProxies(proxies, logs);
    logs.push(`[兼容] 兼容模式解析完成，有效节点: ${result.length} 个`);
    return result;
}

function loadStaticIp(content) {
    const lines = content.split('\n').map(line => line.trim()).filter(line => line);
    for (const line of lines) {
        const parsed = parseSocks5Info(line);
        if (parsed) {
            return parsed;
        }
    }
    return null;
}

function generateYamlHeader() {
    const now = new Date();
    const timestamp = now.getFullYear() + '-' +
        String(now.getMonth() + 1).padStart(2, '0') + '-' +
        String(now.getDate()).padStart(2, '0') + ' ' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0') + ':' +
        String(now.getSeconds()).padStart(2, '0');
    return YAML_HEADER_TEMPLATE.replace('{timestamp}', timestamp);
}

function writeYamlLines(value, indent) {
    const lines = [];
    if (value && typeof value === 'object' && !Array.isArray(value)) {
        for (const [k, v] of Object.entries(value)) {
            const vLines = writeYamlLines(v, indent + 2);
            if (vLines.length === 1 && !vLines[0].startsWith(' ')) {
                lines.push(' '.repeat(indent) + k + ': ' + vLines[0]);
            } else {
                lines.push(' '.repeat(indent) + k + ':');
                lines.push(...vLines);
            }
        }
    } else if (Array.isArray(value)) {
        for (const item of value) {
            const itemLines = writeYamlLines(item, indent + 2);
            if (itemLines.length === 1 && !itemLines[0].startsWith(' ')) {
                lines.push(' '.repeat(indent) + '- ' + itemLines[0]);
            } else {
                lines.push(' '.repeat(indent) + '-');
                lines.push(...itemLines);
            }
        }
    } else {
        lines.push(yamlScalar(value));
    }
    return lines;
}

function generateProxiesSection(proxies, staticIpInfo, staticIpName) {
    const lines = ['proxies:'];
    for (const proxy of proxies) {
        if (proxy.name === staticIpName) {
            continue;
        }
        lines.push('- name: ' + yamlScalar(proxy.name || ''));
        for (const [key, value] of Object.entries(proxy)) {
            if (key === 'name') {
                continue;
            }
            const valLines = writeYamlLines(value, 4);
            if (valLines.length === 1 && !valLines[0].startsWith(' ')) {
                lines.push('  ' + key + ': ' + valLines[0]);
            } else {
                lines.push('  ' + key + ':');
                lines.push(...valLines);
            }
        }
    }
    lines.push('- name: ' + yamlScalar(staticIpName));
    lines.push('  type: socks5');
    lines.push('  server: ' + yamlScalar(staticIpInfo.server));
    lines.push('  port: ' + yamlScalar(staticIpInfo.port));
    lines.push('  username: ' + yamlScalar(staticIpInfo.username));
    lines.push('  password: ' + yamlScalar(staticIpInfo.password));
    lines.push('  udp: true');
    lines.push('  dialer-proxy: ' + yamlScalar('✈️ 前置中转'));
    lines.push('');
    return lines.join('\n');
}

function generateProxyGroups(proxyNames, staticIpName, transitProxies) {
    if (transitProxies === null || transitProxies === undefined) {
        transitProxies = proxyNames;
    }
    const lines = ['proxy-groups:'];
    const urlTestProxies = transitProxies.filter(n => n !== staticIpName);
    lines.push("- name: '✈️ 前置中转-自动'");
    lines.push('  type: url-test');
    lines.push('  url: http://www.gstatic.com/generate_204');
    lines.push('  interval: 300');
    lines.push('  tolerance: 50');
    lines.push('  proxies:');
    for (const name of urlTestProxies) {
        lines.push('  - ' + escapeProxyName(name));
    }
    lines.push("- name: '✈️ 前置中转'");
    lines.push('  type: select');
    lines.push('  proxies:');
    lines.push("  - '✈️ 前置中转-自动'");
    for (const name of transitProxies) {
        lines.push('  - ' + escapeProxyName(name));
    }
    lines.push("- name: '🌍 国外网站'");
    lines.push('  type: select');
    lines.push('  proxies:');
    lines.push("  - '✈️ 前置中转'");
    lines.push('  - DIRECT');
    lines.push("- name: '🏠 静态住宅IP'");
    lines.push('  type: select');
    lines.push('  proxies:');
    const staticName = proxyNames.length > 0 ? proxyNames[proxyNames.length - 1] : staticIpName;
    lines.push('  - ' + escapeProxyName(staticName));
    lines.push("  - '✈️ 前置中转'");
    lines.push("- name: '🤖 AI专用'");
    lines.push('  type: select');
    lines.push('  proxies:');
    lines.push("  - '🏠 静态住宅IP'");
    lines.push("  - '✈️ 前置中转'");
    lines.push('');
    return lines.join('\n');
}

function generateRules() {
    return (
        'rules:\n' +
        '- IP-CIDR,127.0.0.0/8,DIRECT,no-resolve\n' +
        '- IP-CIDR,172.16.0.0/12,DIRECT,no-resolve\n' +
        '- IP-CIDR,192.168.0.0/16,DIRECT,no-resolve\n' +
        '- IP-CIDR,10.0.0.0/8,DIRECT,no-resolve\n' +
        '- IP-CIDR,100.64.0.0/10,DIRECT,no-resolve\n' +
        '- IP-CIDR,224.0.0.0/4,DIRECT,no-resolve\n' +
        '- IP-CIDR,fe80::/10,DIRECT,no-resolve\n' +
        '- IP-CIDR,fc00::/7,DIRECT,no-resolve\n' +
        STATIC_IP_RULES + '\n' +
        '- GEOSITE,CN,DIRECT\n' +
        '- GEOIP,CN,DIRECT,no-resolve\n' +
        STATIC_AI_RULES + '\n' +
        '- MATCH,🌍 国外网站'
    );
}

function generateThreeStageYaml(nodeContent, ipContent, outputFile, includeStaticInTransit) {
    const logs = [];
    logs.push('[步骤1] 加载节点配置文件...');
    const proxies = loadNodesFromYaml(nodeContent, logs);
    if (!proxies || proxies.length === 0) {
        logs.push('[错误] 未能加载任何有效节点');
        return { success: false, logs, yamlContent: '', message: '未能加载任何有效节点' };
    }
    logs.push(`        找到 ${proxies.length} 个有效代理节点`);

    logs.push('[步骤2] 加载静态住宅IP信息...');
    const staticIp = loadStaticIp(ipContent);
    if (!staticIp) {
        logs.push('[错误] 未能加载静态IP信息');
        return { success: false, logs, yamlContent: '', message: '未能加载静态IP信息' };
    }
    logs.push(`        服务器: ${staticIp.server}`);
    logs.push(`        端口: ${staticIp.port}`);

    logs.push('[步骤3] 生成三段式配置...');
    const staticIpName = STATIC_IP_NAME;

    const proxyNames = proxies.map(p => p.name);
    proxyNames.push(staticIpName);

    const transitProxies = includeStaticInTransit ? proxyNames : proxyNames.slice(0, -1);

    const yamlContent = [
        generateYamlHeader(),
        generateProxiesSection(proxies, staticIp, staticIpName),
        generateProxyGroups(proxyNames, staticIpName, transitProxies),
        generateRules()
    ].join('\n');

    logs.push('[步骤4] 配置生成完成');
    logs.push(`[成功] 配置已生成: ${outputFile}`);

    return { success: true, logs, yamlContent, message: '配置生成成功' };
}
