# 0138_SP_ASSESSMENT_CW2_AI
0138_SP_ASSESSMENT_CW2_AI/LLM
# Medical IoT Data Sanitization Gateway (Tier 1.5 & Tier 2)

本项目是针对医疗物联网（Healthcare IoT）防御高级数据投毒攻击（Data Poisoning）的双层清洗网关。通过结合极速规则引擎（$O(1)$）与本地大语言模型（LLMs），实现对原始遥测数据的离线语义清洗，防止被污染的数据进入医疗数据湖（Data Lake）并破坏后续的 AI 训练模型。

## 1. 工程文件已完成内容

目前防守方 AI 核心清洗引擎已全部完工，包含以下核心文件：

* **`main_gateway.py`**: 核心主入口文件。实现了 `DualLayerDefenseGateway` 类，负责将前置规则与 LLM 进行双层路由调度。
* **`pre_filter.py`**: Tier 1.5 极速规则引擎。利用人类生理学极限常识（如心率上限、血氧下限）进行 $O(1)$ 复杂度的脏数据秒杀（耗时 ~0.02ms）。
* **`prompts.py`**: 大模型核心系统提示词。定义了 AI 数据清洗专家的 Persona，并注入了严格的生理学交叉验证规则与 JSON 输出格式约束。
* **`ai_agent.py`**: Tier 2 大模型代理引擎。负责通过本地 API 与 Ollama 进行通信，处理规则引擎无法判断的隐蔽型时间序列攻击。
* **`test_mock.json`**: 测试桩数据。包含了正常数据、暴力投毒和隐蔽投毒三种测试场景。

## 2. 环境配置与依赖

本系统设计为极简依赖，无需复杂的第三方框架：

1.  **Python 版本**: 建议 Python 3.9 或以上版本。
2.  **依赖安装**: 项目仅依赖 Python 原生的 `json`, `time` 库，以及用于 HTTP 请求的 `requests` 库。
    ```bash
    pip install requests
    ```

## 3. 本地 AI 部署步骤 (Ollama)

为了保障患者数据隐私（GDPR 合规），本系统采用完全本地化的本地边缘模型进行推理，不依赖云端 OpenAI 接口。

1.  **安装 Ollama**: 前往 [Ollama 官网](https://ollama.com/) 下载并安装对应系统的客户端。
2.  **拉取轻量级清洗大模型**: 打开终端（Terminal/PowerShell），运行以下命令下载并启动 Qwen 2.5 (1.5B) 轻量化模型：
    ```bash
    ollama run qwen2.5:1.5b
    ```
3.  **后台运行**: 当看到 `>>>` 提示符时，输入 `/bye` 退出交互模式。Ollama 将作为后台服务在本地 `http://localhost:11434` 端口静默运行，等待网关调用。

## 🔌 4. 接口样式 (Python Function Interface)

为了最大化联调效率，当前支持原生 Python 对象直接调用。

### 4.1 初始化与调用示例
```python
from main_gateway import DualLayerDefenseGateway

# 1. 全局初始化（请在系统启动时执行一次，切勿在并发循环中重复初始化）
gateway = DualLayerDefenseGateway(llm_model_name="qwen2.5:1.5b")

# 2. 调用清洗评估函数
decision_result = gateway.evaluate_telemetry(payload)
```

### 4.2 输入 Payload 契约 (Input Schema)
传入的 payload 必须是一个合法的 Python 字典，并由调用方（如 FastAPI 节点）提前拼装好历史滑动窗口：
```python
{
  "request_id": "req_001",
  "device_id": "dev_001",
  "current_data": {
    "metrics": {"heart_rate": 185, "spo2": 98},
    "signal_quality": 0.95
  },
  "history_window": [
    {"heart_rate": 72, "spo2": 98},
    {"heart_rate": 74, "spo2": 98}
  ]
}
```
### 4.3 输出 Response 契约 (Output Schema)
引擎将返回一个严格格式化的字典，指示下游系统是否应将该数据入库（Retain）或丢弃（Discard）：
```python
{
  "request_id": "req_001",
  "device_id": "dev_001",
  "is_poisoned": true, 
  "risk_level": "high",
  "recommended_action": "discard", 
  "confidence_score": 1.0,
  "caught_by": "pre_filter", 
  "latency_ms": 0.02,
  "reasoning_log": "Blocked: Heart rate (280 BPM) violates human physiological limits."
}
```