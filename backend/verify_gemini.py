import os
import time
import sys

# Ensure we can import modules from current directory
sys.path.append(os.getcwd())

try:
    from cv_analyzer import analyze_cv_with_ai, genai_configured
    import google.generativeai as genai
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_config():
    print(f"GenAI Configured: {genai_configured}")
    key = os.getenv("GEMINI_API_KEY")
    if key:
        print(f"API Key present: {key[:5]}...")
        try:
            print("Listing available models...")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f" - {m.name}")
        except Exception as e:
            print(f"Error listing models: {e}")
    else:
        print("API Key MISSING!")

def test_gemini_call():
    print("\n--- Testing Gemini Call ---")
    text = "Juan Perez. Desarrollador Python Senior. 10 años de experiencia. Experto en Django, FastAPI y React. Email: juan@example.com"
    
    try:
        result = analyze_cv_with_ai(text)
        print("Result received from Gemini/Fallback:")
        import json
        # Pretty print partial result
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "contacto" in result and result["contacto"].get("nombre") == "Juan Perez":
            print("\nSUCCESS: Extracted name correctly!")
        else:
            print("\nWARNING: Extraction might have used fallback or failed to parse.")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_config()
    test_gemini_call()
