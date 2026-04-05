import json
import time

class PreFilterGateway:
    """
    Tier 1.5 High-Speed Front-End Rule Engine:
    Intercepts rudimentary 'data poisoning' that defies human physiological limits, protecting the backend LLM from excessive computational load.
    """
    def __init__(self):
        # Define strict rules for physiological limits (adjustable)
        self.rules = {
            "max_heart_rate": 220,
            "min_heart_rate": 30,
            "min_spo2": 60,
            "max_systolic_bp": 220,
            "min_diastolic_bp": 40,
            "min_signal_quality": 0.4
        }

    def evaluate(self, payload: dict) -> dict:
        """
        Takes a JSON dictionary as input and returns a standard decision dictionary
        """
        start_time = time.perf_counter()
        req_id = payload.get("request_id", "unknown")
        dev_id = payload.get("device_id", "unknown")
        
        response = {
            "request_id": req_id,
            "device_id": dev_id,
            "is_poisoned": False,
            "risk_level": "low",
            "recommended_action": "retain",
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

            # Perform a fast pattern match (O(1) complexity)
            if signal_quality < self.rules["min_signal_quality"]:
                response.update({
                    "is_poisoned": True, 
                    "risk_level": "high", 
                    "recommended_action": "discard",
                    "confidence_score": 0.99,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: Signal quality ({signal_quality}) too low. Potential sensor noise or tampering."
                })
            elif hr > self.rules["max_heart_rate"] or hr < self.rules["min_heart_rate"]:
                response.update({
                    "is_poisoned": True, 
                    "risk_level": "high", 
                    "recommended_action": "discard",
                    "confidence_score": 1.0,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: Heart rate ({hr} BPM) violates human physiological limits."
                })
            elif spo2 < self.rules["min_spo2"]:
                response.update({
                    "is_poisoned": True, 
                    "risk_level": "high", 
                    "recommended_action": "discard",
                    "confidence_score": 1.0,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: SpO2 ({spo2}%) is fatally low, likely false data injection."
                })
            elif sys_bp > self.rules["max_systolic_bp"] or dia_bp < self.rules["min_diastolic_bp"]:
                response.update({
                    "is_poisoned": True, 
                    "risk_level": "high", 
                    "recommended_action": "discard",
                    "confidence_score": 1.0,
                    "caught_by": "pre_filter",
                    "reasoning_log": f"Blocked: Blood pressure ({sys_bp}/{dia_bp}) is biologically impossible."
                })

        except Exception as e:
            # If a parsing error occurs, the default action is to pass it on to the next level or log the exception
            response["reasoning_log"] = f"Pre-filter parsing error: {str(e)}"

        # Compute latency
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
            
            result = gateway.evaluate(payload)
            
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except FileNotFoundError:
        print("The file test_mock.json cannot be found. Please ensure it is in the same directory as pre_filter.py.")