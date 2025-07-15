// 全局变量
let currentTab = 'generate';
let systemStatus = {
    healthy: false,
    speechAvailable: false,
    apiCount: 0
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeSystemInfoPanel();
    checkSystemStatus();
    loadStatistics();
    loadHistory();
});

// 初始化应用
function initializeApp() {
    console.log('🎨 PGG情感记忆生成系统 - Web界面初始化');
    
    // 设置默认选项卡
    showTab('generate');
    
    // 启动定时任务
    setInterval(checkSystemStatus, 30000); // 30秒检查一次系统状态
    setInterval(loadStatistics, 60000); // 60秒更新一次统计数据
}

// 设置事件监听器
function setupEventListeners() {
    // 选项卡切换
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tab = this.dataset.tab;
            showTab(tab);
        });
    });
    
    // 生成回忆表单
    document.getElementById('generate-form').addEventListener('submit', function(e) {
        e.preventDefault();
        generateMemory();
    });
    
    // 语音转文本表单
    document.getElementById('speech-form').addEventListener('submit', function(e) {
        e.preventDefault();
        convertSpeechToText();
    });
    
    // 历史记录搜索
    document.getElementById('history-search').addEventListener('input', function() {
        filterHistory(this.value);
    });
    
    // 刷新历史记录
    document.getElementById('refresh-history').addEventListener('click', function() {
        loadHistory();
    });
    
    // 实时录音事件监听器
    document.getElementById('start-recording').addEventListener('click', startRecording);
    document.getElementById('stop-recording').addEventListener('click', stopRecording);
    document.getElementById('clear-recording').addEventListener('click', clearRecording);
    
    // 系统信息面板事件监听器
    document.getElementById('refresh-system-info').addEventListener('click', function() {
        refreshSystemInfo();
    });
    
    document.getElementById('toggle-system-info').addEventListener('click', function() {
        toggleSystemInfoPanel();
    });
}

// 显示指定选项卡
function showTab(tabName) {
    // 隐藏所有选项卡内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // 移除所有选项卡按钮的激活状态
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // 显示指定选项卡内容
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // 激活指定选项卡按钮
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    currentTab = tabName;
    
    // 根据选项卡加载相应数据
    if (tabName === 'history') {
        loadHistory();
    }
}

// 检查系统状态
async function checkSystemStatus() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        systemStatus.healthy = data.status === 'healthy';
        updateSystemStatusUI();
        
        // 检查语音服务状态
        await checkSpeechServiceStatus();
        
    } catch (error) {
        console.error('系统状态检查失败:', error);
        systemStatus.healthy = false;
        updateSystemStatusUI();
    }
}

// 检查语音服务状态
async function checkSpeechServiceStatus() {
    try {
        const response = await fetch('/speech-to-text/status');
        const data = await response.json();
        
        systemStatus.speechAvailable = data.available;
        document.getElementById('speech-status').textContent = data.available ? '可用' : '不可用';
        
    } catch (error) {
        console.error('语音服务状态检查失败:', error);
        systemStatus.speechAvailable = false;
        document.getElementById('speech-status').textContent = '不可用';
    }
}

// 更新系统状态UI
function updateSystemStatusUI() {
    const systemStatusEl = document.getElementById('system-status');
    const apiStatusEl = document.getElementById('api-status');
    
    if (systemStatus.healthy) {
        systemStatusEl.classList.remove('error');
        systemStatusEl.classList.add('success');
        systemStatusEl.querySelector('span').textContent = '系统正常';
    } else {
        systemStatusEl.classList.remove('success');
        systemStatusEl.classList.add('error');
        systemStatusEl.querySelector('span').textContent = '系统异常';
    }
    
    apiStatusEl.querySelector('span').textContent = `API调用: ${systemStatus.apiCount}`;
}

// 加载统计数据
async function loadStatistics() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        document.getElementById('total-memories').textContent = data.total_memories || 0;
        document.getElementById('total-users').textContent = data.total_users || 0;
        document.getElementById('avg-emotion').textContent = (data.avg_emotion_score || 0).toFixed(1) + '%';
        
        systemStatus.apiCount = data.api_calls || 0;
        updateSystemStatusUI();
        
    } catch (error) {
        console.error('统计数据加载失败:', error);
    }
}

// 生成回忆
async function generateMemory() {
    const text = document.getElementById('memory-text').value;
    const userId = document.getElementById('user-id').value || 'anonymous';
    const emotionOverride = document.getElementById('emotion-override').value;
    
    if (!text.trim()) {
        showResult('generate-result', '请输入文本内容', 'error');
        return;
    }
    
    const resultDiv = document.getElementById('generate-result');
    resultDiv.innerHTML = '<div class="loading"></div>正在生成回忆...';
    resultDiv.classList.add('show');
    
    try {
        const requestData = {
            text: text,
            user_id: userId
        };
        
        if (emotionOverride) {
            requestData.emotion_override = emotionOverride;
        }
        
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayMemoryResult(data);
            // 重新加载统计数据和历史记录
            loadStatistics();
            if (currentTab === 'history') {
                loadHistory();
            }
        } else {
            showResult('generate-result', `生成失败: ${data.error || '未知错误'}`, 'error');
        }
        
    } catch (error) {
        console.error('生成回忆失败:', error);
        showResult('generate-result', `生成失败: ${error.message}`, 'error');
    }
}

// 显示回忆生成结果
function displayMemoryResult(data) {
    const resultDiv = document.getElementById('generate-result');
    
    let html = `
        <div class="memory-result">
            <h3>✨ 回忆生成成功</h3>
            <div class="memory-details">
                <p><strong>回忆ID:</strong> ${data.id}</p>
                <p><strong>用户ID:</strong> ${data.user_id}</p>
                <p><strong>创建时间:</strong> ${new Date(data.created_at).toLocaleString()}</p>
                <p><strong>原始文本:</strong> ${data.text}</p>
                <p><strong>情感分析:</strong> 
                    <span class="emotion-badge">${data.emotion.primary_emotion}</span> 
                    (${(data.emotion.confidence * 100).toFixed(1)}%)
                </p>
                <p><strong>情感描述:</strong> ${data.emotion.description}</p>
                ${data.image_url ? `
                    <div class="image-preview">
                        <p><strong>生成的图像:</strong></p>
                        <img src="${data.image_url}" alt="Generated Memory Image" style="max-width: 300px; border-radius: 8px;">
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
    resultDiv.classList.add('show', 'result-success');
}

// 语音转文本
async function convertSpeechToText() {
    const fileInput = document.getElementById('audio-file');
    const language = document.getElementById('language').value;
    
    if (!fileInput.files[0]) {
        showResult('speech-result', '请选择音频文件', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    const maxSize = 25 * 1024 * 1024; // 25MB
    
    if (file.size > maxSize) {
        showResult('speech-result', '文件大小超过25MB限制', 'error');
        return;
    }
    
    const resultDiv = document.getElementById('speech-result');
    resultDiv.innerHTML = '<div class="loading"></div>正在转换语音...';
    resultDiv.classList.add('show');
    
    try {
        const formData = new FormData();
        formData.append('audio', file);
        formData.append('language', language);
        
        const response = await fetch('/speech-to-text', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySpeechResult(data);
        } else {
            showResult('speech-result', `转换失败: ${data.error || '未知错误'}`, 'error');
        }
        
    } catch (error) {
        console.error('语音转文本失败:', error);
        showResult('speech-result', `转换失败: ${error.message}`, 'error');
    }
}

// 显示语音转文本结果
function displaySpeechResult(data) {
    const resultDiv = document.getElementById('speech-result');
    
    let html = `
        <div class="speech-result">
            <h3>🎤 语音转文本成功</h3>
            <div class="speech-details">
                <p><strong>转换ID:</strong> ${data.id}</p>
                <p><strong>语言:</strong> ${data.language}</p>
                <p><strong>置信度:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                <p><strong>转换时间:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                <p><strong>转换结果:</strong></p>
                <div class="transcription-text">
                    ${data.transcription}
                </div>
                <button onclick="useTranscriptionForMemory('${data.transcription}')" class="btn btn-primary">
                    <i class="fas fa-magic"></i> 使用此文本生成回忆
                </button>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
    resultDiv.classList.add('show', 'result-success');
}

// 使用转录文本生成回忆
function useTranscriptionForMemory(text) {
    // 切换到生成回忆选项卡
    showTab('generate');
    
    // 填充文本框
    document.getElementById('memory-text').value = text;
    
    // 滚动到表单位置
    document.getElementById('generate-form').scrollIntoView({ behavior: 'smooth' });
}

// 加载历史记录
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        displayHistory(data.memories || []);
        
    } catch (error) {
        console.error('历史记录加载失败:', error);
        document.getElementById('history-list').innerHTML = '<p>历史记录加载失败</p>';
    }
}

// 显示历史记录
function displayHistory(memories) {
    const historyList = document.getElementById('history-list');
    
    if (memories.length === 0) {
        historyList.innerHTML = '<p>暂无历史记录</p>';
        return;
    }
    
    let html = '';
    memories.forEach(memory => {
        html += `
            <div class="history-item" data-id="${memory.id}">
                <h4>
                    ${memory.text.substring(0, 50)}${memory.text.length > 50 ? '...' : ''}
                    <span class="emotion-badge">${memory.emotion.primary_emotion}</span>
                </h4>
                <div class="timestamp">
                    ${new Date(memory.created_at).toLocaleString()}
                </div>
                <div class="content">
                    <p><strong>用户:</strong> ${memory.user_id}</p>
                    <p><strong>情感:</strong> ${memory.emotion.primary_emotion} (${(memory.emotion.confidence * 100).toFixed(1)}%)</p>
                    <p><strong>描述:</strong> ${memory.emotion.description}</p>
                    ${memory.image_url ? `
                        <div class="image-preview">
                            <img src="${memory.image_url}" alt="Memory Image">
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    historyList.innerHTML = html;
}

// 过滤历史记录
function filterHistory(searchTerm) {
    const historyItems = document.querySelectorAll('.history-item');
    
    historyItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        const match = text.includes(searchTerm.toLowerCase());
        item.style.display = match ? 'block' : 'none';
    });
}

// 显示结果
function showResult(elementId, message, type = 'info') {
    const resultDiv = document.getElementById(elementId);
    resultDiv.innerHTML = message;
    resultDiv.classList.add('show');
    
    // 移除之前的类型类
    resultDiv.classList.remove('result-success', 'result-error', 'result-warning');
    
    // 添加新的类型类
    if (type === 'success') {
        resultDiv.classList.add('result-success');
    } else if (type === 'error') {
        resultDiv.classList.add('result-error');
    } else if (type === 'warning') {
        resultDiv.classList.add('result-warning');
    }
}

// API测试函数
async function testHealth() {
    const resultDiv = document.getElementById('health-result');
    resultDiv.innerHTML = '<div class="loading"></div>测试中...';
    
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        resultDiv.innerHTML = `
            <strong>系统健康状态:</strong>
            ${JSON.stringify(data, null, 2)}
        `;
        
    } catch (error) {
        resultDiv.innerHTML = `错误: ${error.message}`;
    }
}

async function testSpeechStatus() {
    const resultDiv = document.getElementById('speech-service-result');
    resultDiv.innerHTML = '<div class="loading"></div>测试中...';
    
    try {
        const response = await fetch('/speech-to-text/status');
        const data = await response.json();
        
        resultDiv.innerHTML = `
            <strong>语音服务状态:</strong>
            ${JSON.stringify(data, null, 2)}
        `;
        
    } catch (error) {
        resultDiv.innerHTML = `错误: ${error.message}`;
    }
}

async function testStats() {
    const resultDiv = document.getElementById('stats-result');
    resultDiv.innerHTML = '<div class="loading"></div>测试中...';
    
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        resultDiv.innerHTML = `
            <strong>系统统计:</strong>
            ${JSON.stringify(data, null, 2)}
        `;
        
    } catch (error) {
        resultDiv.innerHTML = `错误: ${error.message}`;
    }
}

// 工具函数
function formatDate(dateString) {
    return new Date(dateString).toLocaleString('zh-CN');
}

function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// 导出函数供HTML使用
window.testHealth = testHealth;
window.testSpeechStatus = testSpeechStatus;
window.testStats = testStats;
window.useTranscriptionForMemory = useTranscriptionForMemory;

// ==================== 实时录音功能 ====================

// 录音相关全局变量
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let recordingStartTime = 0;
let recordingTimer = null;
let audioStream = null;

// 检查浏览器是否支持录音
function isBrowserSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);
}

// 获取麦克风权限
async function requestMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 16000
            } 
        });
        return stream;
    } catch (error) {
        console.error('获取麦克风权限失败:', error);
        throw error;
    }
}

// 开始录音
async function startRecording() {
    // 检查浏览器支持
    if (!isBrowserSupported()) {
        showPermissionNotice('您的浏览器不支持录音功能，请使用现代浏览器如Chrome或Firefox');
        return;
    }
    
    try {
        // 显示准备状态
        updateRecordingStatus('准备中...', false);
        
        // 获取麦克风权限
        audioStream = await requestMicrophonePermission();
        
        // 初始化媒体录制器
        mediaRecorder = new MediaRecorder(audioStream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        
        // 重置音频数据
        audioChunks = [];
        
        // 设置录音事件监听器
        mediaRecorder.ondataavailable = function(event) {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = function() {
            processRecordedAudio();
        };
        
        // 开始录音
        mediaRecorder.start(1000); // 每秒收集一次数据
        isRecording = true;
        recordingStartTime = Date.now();
        
        // 更新UI状态
        updateRecordingUI(true);
        updateRecordingStatus('正在录音...', true);
        
        // 开始计时器
        startRecordingTimer();
        
        console.log('📢 开始录音');
        
    } catch (error) {
        console.error('开始录音失败:', error);
        let errorMessage = '开始录音失败';
        
        if (error.name === 'NotAllowedError') {
            errorMessage = '麦克风权限被拒绝，请允许访问麦克风后重试';
        } else if (error.name === 'NotFoundError') {
            errorMessage = '未找到麦克风设备，请检查设备连接';
        } else if (error.name === 'NotSupportedError') {
            errorMessage = '您的浏览器不支持录音功能';
        }
        
        showPermissionNotice(errorMessage);
        resetRecordingState();
    }
}

// 停止录音
function stopRecording() {
    if (!isRecording || !mediaRecorder) {
        return;
    }
    
    try {
        // 停止录音
        mediaRecorder.stop();
        isRecording = false;
        
        // 停止媒体流
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
            audioStream = null;
        }
        
        // 更新UI状态
        updateRecordingUI(false);
        updateRecordingStatus('处理中...', false);
        
        // 停止计时器
        stopRecordingTimer();
        
        console.log('⏹️ 录音已停止');
        
    } catch (error) {
        console.error('停止录音失败:', error);
        showPermissionNotice('停止录音失败，请重试');
        resetRecordingState();
    }
}

// 处理录音数据
async function processRecordedAudio() {
    if (audioChunks.length === 0) {
        showPermissionNotice('没有录制到音频数据，请重试');
        resetRecordingState();
        return;
    }
    
    try {
        // 创建音频blob
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        // 检查音频大小
        const maxSize = 25 * 1024 * 1024; // 25MB
        if (audioBlob.size > maxSize) {
            showPermissionNotice('录音文件过大，请录制较短的音频');
            resetRecordingState();
            return;
        }
        
        console.log(`🎵 录音完成，文件大小: ${(audioBlob.size / 1024 / 1024).toFixed(2)}MB`);
        
        // 发送到服务器转换
        await sendAudioToServer(audioBlob);
        
    } catch (error) {
        console.error('处理录音数据失败:', error);
        showPermissionNotice('处理录音数据失败，请重试');
        resetRecordingState();
    }
}

// 发送音频到服务器
async function sendAudioToServer(audioBlob) {
    const language = document.getElementById('realtime-language').value;
    
    try {
        updateRecordingStatus('正在转换...', false);
        
        // 创建FormData
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('language', language);
        
        // 发送请求
        const response = await fetch('/speech-to-text', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayRealtimeResult(data);
            updateRecordingStatus('转换完成', false);
        } else {
            throw new Error(data.message || '转换失败');
        }
        
    } catch (error) {
        console.error('音频转换失败:', error);
        showPermissionNotice(`转换失败: ${error.message}`);
        updateRecordingStatus('转换失败', false);
    } finally {
        resetRecordingState();
    }
}

// 显示实时转换结果
function displayRealtimeResult(data) {
    const resultDiv = document.getElementById('realtime-text');
    
    if (data.text && data.text.trim()) {
        resultDiv.textContent = data.text;
        resultDiv.classList.add('has-text');
        
        // 显示详细信息
        const confidence = (data.confidence * 100).toFixed(1);
        const service = data.service || '未知';
        const language = data.language || '未知';
        
        console.log(`🎯 转换成功: ${data.text}`);
        console.log(`📊 置信度: ${confidence}%, 服务: ${service}, 语言: ${language}`);
        
        // 滚动到结果区域
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } else {
        resultDiv.textContent = '未识别到语音内容，请重试';
        resultDiv.classList.remove('has-text');
    }
}

// 清除录音
function clearRecording() {
    // 如果正在录音，先停止
    if (isRecording) {
        stopRecording();
        return;
    }
    
    // 重置所有状态
    resetRecordingState();
    
    // 清除结果显示
    const resultDiv = document.getElementById('realtime-text');
    resultDiv.textContent = '';
    resultDiv.classList.remove('has-text');
    
    // 隐藏权限提示
    hidePermissionNotice();
    
    console.log('🗑️ 录音已清除');
}

// 重置录音状态
function resetRecordingState() {
    isRecording = false;
    recordingStartTime = 0;
    audioChunks = [];
    
    if (mediaRecorder) {
        mediaRecorder = null;
    }
    
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }
    
    updateRecordingUI(false);
    updateRecordingStatus('准备录音', false);
    stopRecordingTimer();
}

// 更新录音UI状态
function updateRecordingUI(recording) {
    const startBtn = document.getElementById('start-recording');
    const stopBtn = document.getElementById('stop-recording');
    const indicator = document.getElementById('recording-indicator');
    
    startBtn.disabled = recording;
    stopBtn.disabled = !recording;
    
    if (recording) {
        indicator.classList.add('recording');
    } else {
        indicator.classList.remove('recording');
    }
}

// 更新录音状态显示
function updateRecordingStatus(status, recording) {
    const statusEl = document.getElementById('recording-status');
    statusEl.textContent = status;
    
    if (recording) {
        statusEl.classList.add('recording');
    } else {
        statusEl.classList.remove('recording');
    }
}

// 开始录音计时器
function startRecordingTimer() {
    const timeEl = document.getElementById('recording-time');
    timeEl.classList.add('recording');
    
    recordingTimer = setInterval(() => {
        const elapsed = Date.now() - recordingStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        timeEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

// 停止录音计时器
function stopRecordingTimer() {
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    
    const timeEl = document.getElementById('recording-time');
    timeEl.classList.remove('recording');
}

// 显示权限提示
function showPermissionNotice(message) {
    // 移除现有提示
    hidePermissionNotice();
    
    const notice = document.createElement('div');
    notice.className = 'permission-notice';
    notice.innerHTML = `<i class="fas fa-exclamation-triangle"></i><span>${message}</span>`;
    
    const realtimeControls = document.querySelector('.realtime-controls');
    realtimeControls.parentNode.insertBefore(notice, realtimeControls);
}

// 隐藏权限提示
function hidePermissionNotice() {
    const existingNotice = document.querySelector('.permission-notice');
    if (existingNotice) {
        existingNotice.remove();
    }
}

// 页面卸载时清理资源
window.addEventListener('beforeunload', function() {
    if (isRecording) {
        stopRecording();
    }
});

// ===== 系统信息面板功能 =====

// 初始化系统信息面板
function initializeSystemInfoPanel() {
    refreshSystemInfo();
    
    // 定时刷新系统信息（每2分钟）
    setInterval(refreshSystemInfo, 120000);
}

// 刷新系统信息
async function refreshSystemInfo() {
    const refreshBtn = document.getElementById('refresh-system-info');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 刷新中...';
    }
    
    try {
        // 并行获取所有系统信息
        const [healthData, configData, statsData] = await Promise.all([
            fetch('/health').then(r => r.json()),
            fetch('/config/status').then(r => r.json()),
            fetch('/stats').then(r => r.json())
        ]);
        
        // 更新系统状态信息
        updateSystemStatusInfo(healthData, configData);
        
        // 更新API服务状态
        updateApiStatusInfo(configData);
        
        // 更新模型状态
        updateModelStatusInfo(healthData, configData);
        
        // 更新系统配置
        updateSystemConfigInfo(configData);
        
        console.log('系统信息刷新完成');
        
    } catch (error) {
        console.error('刷新系统信息失败:', error);
        showSystemInfoError('刷新失败，请稍后重试');
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 刷新';
        }
    }
}

// 更新系统状态信息
function updateSystemStatusInfo(healthData, configData) {
    // 系统版本
    document.getElementById('system-version').textContent = healthData.version || 'PGG v1.0.0';
    
    // 运行模式
    const debugMode = configData.debug_mode || false;
    document.getElementById('debug-mode').textContent = debugMode ? '开发模式' : '生产模式';
    
    // 存储模式
    document.getElementById('storage-mode').textContent = configData.storage_mode || '本地存储';
    
    // CPU模式
    document.getElementById('cpu-mode').textContent = configData.cpu_mode ? '启用' : '禁用';
}

// 更新API服务状态
function updateApiStatusInfo(configData) {
    const apiStatuses = configData.api_statuses || {};
    
    // OpenAI状态
    updateApiStatusElement('openai-status', apiStatuses.openai || false);
    
    // 科大讯飞语音状态
    updateApiStatusElement('iflytek-speech-status', apiStatuses.iflytek_speech || false);
    
    // 科大讯飞图像状态
    updateApiStatusElement('iflytek-image-status', apiStatuses.iflytek_image || false);
    
    // 科大讯飞性别年龄识别状态
    updateApiStatusElement('iflytek-gender-age-status', apiStatuses.iflytek_gender_age || false);
}

// 更新单个API状态元素
function updateApiStatusElement(elementId, isActive) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = `info-value api-status ${isActive ? 'active' : 'inactive'}`;
        element.innerHTML = `<i class="fas fa-circle"></i> ${isActive ? '已配置' : '未配置'}`;
    }
}

// 更新模型状态
function updateModelStatusInfo(healthData, configData) {
    const modelStatuses = configData.model_statuses || {};
    
    // 情感分析模型
    updateModelStatusElement('emotion-model-status', modelStatuses.emotion || true);
    
    // 图像生成模型
    updateModelStatusElement('image-model-status', modelStatuses.image || true);
    
    // 语音识别模型
    updateModelStatusElement('speech-model-status', modelStatuses.speech || true);
    
    // 可用模型数量
    const availableCount = Object.values(modelStatuses).filter(Boolean).length || 4;
    document.getElementById('available-models-count').textContent = availableCount;
}

// 更新单个模型状态元素
function updateModelStatusElement(elementId, isAvailable) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = `info-value model-status ${isAvailable ? 'available' : 'unavailable'}`;
        element.innerHTML = `<i class="fas fa-circle"></i> ${isAvailable ? '可用' : '不可用'}`;
    }
}

// 更新系统配置信息
function updateSystemConfigInfo(configData) {
    // 准确率优先
    const accuracyPriority = configData.accuracy_priority || true;
    document.getElementById('accuracy-priority').textContent = accuracyPriority ? '启用' : '禁用';
    
    // 最大内存
    const maxMemory = configData.max_memory || '512MB';
    document.getElementById('max-memory').textContent = maxMemory;
    
    // 批处理大小
    const batchSize = configData.batch_size || 1;
    document.getElementById('batch-size').textContent = batchSize;
    
    // 服务端口
    const serverPort = configData.server_port || 5000;
    document.getElementById('server-port').textContent = serverPort;
}

// 切换系统信息面板展开/收起状态
function toggleSystemInfoPanel() {
    const panel = document.querySelector('.system-info-panel');
    const toggleBtn = document.getElementById('toggle-system-info');
    const btnIcon = toggleBtn.querySelector('i');
    const btnText = toggleBtn.querySelector('span');
    
    if (panel.classList.contains('collapsed')) {
        // 展开面板
        panel.classList.remove('collapsed');
        toggleBtn.classList.remove('collapsed');
        btnIcon.className = 'fas fa-chevron-up';
        btnText.textContent = '收起详情';
    } else {
        // 收起面板
        panel.classList.add('collapsed');
        toggleBtn.classList.add('collapsed');
        btnIcon.className = 'fas fa-chevron-down';
        btnText.textContent = '展开详情';
    }
}

// 显示系统信息错误
function showSystemInfoError(message) {
    const infoGrid = document.querySelector('.info-grid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'info-loading';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <p>${message}</p>
    `;
    
    // 临时替换内容
    const originalContent = infoGrid.innerHTML;
    infoGrid.innerHTML = errorDiv.outerHTML;
    
    // 3秒后恢复原内容
    setTimeout(() => {
        infoGrid.innerHTML = originalContent;
    }, 3000);
} 