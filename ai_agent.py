# ai_agent.py
import json
import time
import requests
from prompts import MEDICAL_SECURITY_SYSTEM_PROMPT

class LlamaDefenseAgent:
    def __init__(self, model_name="qwen2.5:1.5b"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"

    def evaluate_with_llm(self, payload: dict) -> dict:
        """Calls a local AI model to perform semantic inference and returns a strictly merged JSON"""
        start_time = time.perf_counter()
        
        # Compile the user prompt to be sent to the large model (convert the JSON into a string to feed to it)
        user_prompt = f"Analyze the following IoT telemetry payload:\n{json.dumps(payload, indent=2)}"
        
        request_data = {
            "model": self.model_name,
            "system": MEDICAL_SECURITY_SYSTEM_PROMPT,
            "prompt": user_prompt,
            "stream": False,
            "format": "json"
        }

        try:
            # Send a request to Ollama on the local backend
            response = requests.post(self.api_url, json=request_data)
            response.raise_for_status()
            
            llm_reply_str = response.json().get("response", "{}")
            decision_data = json.loads(llm_reply_str)
            
        except Exception as e:
            decision_data = {
                "is_attack": False,
                "risk_level": "low",
                "recommended_action": "allow",
                "confidence_score": 0.0,
                "reasoning_log": f"LLM Exception triggered fail-open: {str(e)}"
            }

        # LLM latency calculation
        end_time = time.perf_counter()
        latency = round((end_time - start_time) * 1000, 4)
        
        final_response = {
            "request_id": payload.get("request_id", "unknown"),
            "device_id": payload.get("device_id", "unknown"),
            "is_attack": decision_data.get("is_attack", False),
            "risk_level": decision_data.get("risk_level", "low"),
            "recommended_action": decision_data.get("recommended_action", "allow"),
            "confidence_score": decision_data.get("confidence_score", 0.0),
            "caught_by": "llm_agent" if decision_data.get("is_attack") else "none",
            "latency_ms": latency,
            "reasoning_log": decision_data.get("reasoning_log", "")
        }
        
        return final_response
    
# ==========================================
# Code to launch local large-scale model inference testing
# ==========================================
if __name__ == "__main__":
    # Initialisation
    print("Connecting to local qwen2.5:1.5b")
    agent = LlamaDefenseAgent(model_name="qwen2.5:1.5b")

    try:
        with open("test_mock.json", "r", encoding="utf-8") as f:
            mock_data_list = json.load(f)
            
        print("Initiating Tier 2 (LLM Agent) deep reasoning test\n" + "="*60)
        
        for index, payload in enumerate(mock_data_list):
            print(f"\nSubmitting scene {index + 1} to the large model: {payload.get('_description', '')}")
            print("AI is deep in thought (apparently, simply swapping 'loading' for 'thinking' is enough to set up a cutting-edge AI start-up)...")
            
            result = agent.evaluate_with_llm(payload)
            
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 40)
            
    except FileNotFoundError:
        print("Warning: The file `test_mock.json` cannot be found. Please ensure it is in the same directory.")