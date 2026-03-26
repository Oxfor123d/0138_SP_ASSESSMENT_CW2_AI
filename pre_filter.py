import json
import time

class PreFilterGateway:
    """
    Tier 1.5 极速前置规则引擎：
    拦截违背人类生理极限的低级“数据投毒”，保护后端 LLM 不被消耗算力。
    """
    def __init__(self):
        # 定义生理极限硬性规则 (可根据医学常识微调)
        self.rules = {
            "max_heart_rate": 220,
            "min_heart_rate": 30,
            "min_spo2": 60,
            "max_systolic_bp": 220,
            "min_diastolic_bp": 40,
            "min_signal_quality": 0.4  # 信号质量太低视为无效/噪音数据
        }

    def evaluate(self, payload: dict) -> dict:
        """
        核心评估函数：输入 JSON 字典，输出标准判决字典
        """
        start_time = time.perf_counter()  # 开启高精度计时器

        # 1. 提取基础信息
        req_id = payload.get("request_id", "unknown")
        dev_id = payload.get("device_id", "unknown")
        
        # 默认返回模板 (假设放行，交由下一级 LLM 处理)
        response = {
            "request_id": req_id,
            "device_id": dev_id,
            "action": "allow",
            "confidence_score": 0.0,
            "caught_by": "none",
            "latency_ms": 0.0,
            "reasoning_log": "Data within physiological limits. Passed to LLM for semantic analysis."
        }

        try:
            current_data = payload.get("current_data", {})
            metrics = current_data.get("metrics", {})
            hr = metrics.get("heart_rate", 0)
            spo2 = metrics.get("spo2", 0)
            sys_bp = metrics.get("systolic_bp", 0)
            dia_bp = metrics.get("diastolic_bp", 0)
            signal_quality = current_data.get("signal_quality", 1.0)

            # 2. 执行极速规则匹配 (O(1) 复杂度)
            if signal_quality < self.rules["min_signal_quality"]:
                response.update({
                    "action": "block",
                    "confidence_score": 0.99,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: Signal quality ({signal_quality}) too low. Potential sensor noise or tampering."
                })
            elif hr > self.rules["max_heart_rate"] or hr < self.rules["min_heart_rate"]:
                response.update({
                    "action": "block",
                    "confidence_score": 1.0,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: Heart rate ({hr} BPM) violates human physiological limits."
                })
            elif spo2 < self.rules["min_spo2"]:
                response.update({
                    "action": "block",
                    "confidence_score": 1.0,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: SpO2 ({spo2}%) is fatally low, likely false data injection."
                })
            elif sys_bp > self.rules["max_systolic_bp"] or dia_bp < self.rules["min_diastolic_bp"]:
                response.update({
                    "action": "block",
                    "confidence_score": 1.0,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: Blood pressure ({sys_bp}/{dia_bp}) is biologically impossible."
                })

        except Exception as e:
            # 容错处理：如果解析出错，默认放行交由下一级或记录异常
            response["reasoning_log"] = f"Pre-filter parsing error: {str(e)}"

        # 3. 计算延迟并返回
        end_time = time.perf_counter()
        response["latency_ms"] = round((end_time - start_time) * 1000, 4)
        return response


if __name__ == "__main__":
    gateway = PreFilterGateway()

    try:
        with open("test_mock.json", "r", encoding="utf-8") as f:
            mock_data_list = json.load(f)
            
        print("Testing the pre-filter engine...\n" + "="*50)
        
        for index, payload in enumerate(mock_data_list):
            print(f"\nTesting Scenario {index + 1}: {payload.get('_description', '')}")
            
            # 把数据喂给引擎
            result = gateway.evaluate(payload)
            
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except FileNotFoundError:
        print("The file test_mock.json cannot be found. Please ensure it is in the same directory as pre_filter.py.")