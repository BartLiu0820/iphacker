// 全局状态
let nodeFile = null;
let staticIpFile = null;

// DOM元素（延迟获取，确保DOM已就绪）
function getEl(id) { return document.getElementById(id); }

let uploadArea, fileInput, fileList, generateBtn, outputName;
let statusCard, statusText, statusDot, logContainer, previewCard, previewContent;
let logHeader, logBody, logToggle;

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
    logHeader = getEl('logHeader');
    logBody = getEl('logBody');
    logToggle = getEl('logToggle');
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

    // 日志折叠/展开
    if (logHeader && logBody && logToggle) {
        logHeader.addEventListener('click', () => {
            const isHidden = logBody.hasAttribute('hidden');
            if (isHidden) {
                logBody.removeAttribute('hidden');
                logToggle.textContent = '▼';
            } else {
                logBody.setAttribute('hidden', '');
                logToggle.textContent = '▶';
            }
        });
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

// 确保文件名带有 .yaml 扩展名
function ensureYamlExt(name) {
    if (!name) return '三段式配置文件.yaml';
    const trimmed = name.trim();
    if (trimmed.endsWith('.yaml') || trimmed.endsWith('.yml')) return trimmed;
    return trimmed + '.yaml';
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
        addFileItem(nodeFile.name, '\u{1F4C4}', 'node');
    }

    if (staticIpFile) {
        addFileItem(staticIpFile.name, '\u{1F4CB}', 'static');
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

    const outputFile = ensureYamlExt(outputName.value);

    generateBtn.disabled = true;
    const btnText = document.querySelector('.btn-text');
    const btnLoading = document.querySelector('.btn-loading');
    if (btnText) btnText.hidden = true;
    if (btnLoading) btnLoading.hidden = false;

    statusCard.hidden = false;
    if (statusText) statusText.textContent = '生成中...';
    if (statusDot) statusDot.style.background = '#f59e0b';

    try {
        // 直接调用生成器（不再通过 fetch 请求后端）
        const result = generateThreeStageYaml(
            nodeFile.content,
            staticIpFile.content,
            outputFile,
            false
        );

        // 渲染日志
        if (result.logs && result.logs.length > 0) {
            result.logs.forEach(msg => log(msg));
        }

        if (result.success) {
            if (statusText) statusText.textContent = '生成成功！';
            if (statusDot) statusDot.style.background = '#10b981';

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
    const outputFile = ensureYamlExt(outName ? outName.value : '');

    const blob = new Blob([content], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = outputFile;
    a.click();
    URL.revokeObjectURL(url);
}
