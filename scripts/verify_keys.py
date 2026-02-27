import os
import requests
from dotenv import load_dotenv

def check_key(name: str, key_val: str, expected_prefix: str = "") -> str:
    if not key_val:
        return "❌ Missing"
    if key_val.startswith("placeholder_"):
        return "⚠️ Placeholder (Requires real key for full functionality)"
    if expected_prefix and not key_val.startswith(expected_prefix):
        return f"❓ Unusual format (Expected prefix: {expected_prefix})"
    return "✅ Present"

def main():
    print("===========================================")
    print("      BrandGuard API Key Verification      ")
    print("===========================================\n")
    
    env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
    if not os.path.exists(env_path):
        print(f"❌ backend/.env file not found at {env_path}")
        print("Please copy backend/.env.example to backend/.env and add your keys.")
        return
        
    load_dotenv(env_path)
    
    keys_to_check = [
        ("SENSO_GEO_API_KEY", ""),
        ("SENSO_SDK_API_KEY", ""),
        ("TAVILY_API_KEY", "tvly-"),
        ("NEO4J_PASSWORD", ""),
        ("YUTORI_API_KEY", ""),
        ("MODULATE_API_KEY", ""),
        ("OPENAI_API_KEY", "sk-")
    ]
    
    all_ready = True
    for key_name, expected_prefix in keys_to_check:
        val = os.getenv(key_name, "")
        status = check_key(key_name, val, expected_prefix)
        print(f"{key_name:<20}: {status}")
        if "❌" in status or "⚠️" in status:
            all_ready = False
            
    print("\n===========================================")
    if all_ready:
        print("✅ All required API keys are present and look good!")
    else:
        print("⚠️ Some keys are missing or placeholders. Update backend/.env")
    print("===========================================\n")

if __name__ == "__main__":
    main()
