import json
import time

from pre_filter import PreFilterGateway
from ai_agent import LlamaDefenseAgent

class DualLayerDefenseGateway:

    def __init__(self, llm_model_name="qwen2.5:1.5b"):
        print("Initialisation")
        print(" Loading the Tier 1.5 High-Speed Rules Engine")
        self.rule_engine = PreFilterGateway()
        
        print(f"Loading the Tier 2 semantic analysis engine ({llm_model_name})...")
        self.llm_engine = LlamaDefenseAgent(model_name=llm_model_name)

    def evaluate_telemetry(self, payload: dict) -> dict:
        """Core routing and evaluation logic"""
        total_start_time = time.perf_counter()

        # The Pre-filter
        rule_result = self.rule_engine.evaluate(payload)

        # Short-circuit Interception
        # If the rule engine directly classifies an input as an attack (such as a malicious injection with a heart rate of 280), it will be intercepted immediately, thereby avoiding any waste of LLM computational resources.
        if rule_result.get("recommended_action") == "block":
            total_end_time = time.perf_counter()
            rule_result["latency_ms"] = round((total_end_time - total_start_time) * 1000, 4)
            return rule_result


        # The AI Agent
        # Only data approved by the rules engine will be fed into the large model for contextual cross-validation
        llm_result = self.llm_engine.evaluate_with_llm(payload)

        # Cumulative total delay 
        total_end_time = time.perf_counter()
        llm_result["latency_ms"] = round((total_end_time - total_start_time) * 1000, 4)
        
        return llm_result


if __name__ == "__main__":
    # Instantiate the final gateway
    gateway = DualLayerDefenseGateway(llm_model_name="qwen2.5:1.5b")

    try:
        with open("test_mock.json", "r", encoding="utf-8") as f:
            mock_data_list = json.load(f)
            
        print("\n" + "="*60)
        print("Practical Testing of a Dual-Layer Convergence Gateway")
        print("="*60)
        
        for index, payload in enumerate(mock_data_list):
            print(f"\nProcessing data packets {index + 1}: {payload.get('_description', '')}")
            
            start = time.time()
            result = gateway.evaluate_telemetry(payload)
            end = time.time()
            
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("caught_by") == "pre_filter":
                print(f"The pre-processing rule engine has already filtered out this threat. Time taken: {result.get('latency_ms')} ms")
            elif result.get("caught_by") == "llm_agent":
                print(f"The LLM engine has identified this threat. Time taken: {result.get('latency_ms')} ms")
            else:
                print(f"[Approved] Data compliant, passed dual-layer verification. Time taken: {result.get('latency_ms')} ms")
                
            print("-" * 40)
            
    except FileNotFoundError:
        print("Warning: The file `test_mock.json` cannot be found. Please ensure it is in the same directory.")