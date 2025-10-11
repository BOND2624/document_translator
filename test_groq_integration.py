#!/usr/bin/env python3
"""
Quick test to verify Groq integration is working
"""

import os
from dotenv import load_dotenv

# Load environment variables from multiple possible locations
load_dotenv('.env')  # Load from .env first
load_dotenv('config.env')  # Then load from config.env if it exists

def test_groq_integration():
    """Test Groq API integration"""
    
    print("🧪 TESTING GROQ INTEGRATION")
    print("=" * 50)
    
    # Set Groq as provider
    os.environ['LLM_PROVIDER'] = 'groq'
    
    try:
        from src.config import Config
        
        # Check if Groq API key is configured
        groq_key = Config.GROQ_API_KEY
        if not groq_key or groq_key == "your_groq_api_key_here":
            print("❌ Groq API key not configured")
            print("💡 Get your FREE API key from: https://console.groq.com/keys")
            print("📝 Add it to config.env as: GROQ_API_KEY=your_actual_key")
            return False
        
        print(f"✅ Groq API key found: {groq_key[:8]}...")
        
        # Test LLM creation
        print("🔧 Creating Groq LLM instance...")
        llm = Config.create_llm()
        print(f"✅ LLM created successfully: {type(llm).__name__}")
        
        # Test simple translation
        print("🌐 Testing simple translation...")
        test_prompt = "Translate this to Spanish: Hello, how are you today?"
        
        try:
            response = llm.invoke(test_prompt)
            translated_text = response.content.strip()
            print(f"✅ Translation test successful!")
            print(f"   Input: Hello, how are you today?")
            print(f"   Output: {translated_text}")
            
            return True
            
        except Exception as e:
            print(f"❌ Translation test failed: {str(e)}")
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Try: pip install groq langchain-groq")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_groq_integration()
    
    if success:
        print("\n🎉 GROQ INTEGRATION TEST PASSED!")
        print("✅ Ready to run full pipeline with: python test_complete_pipeline.py")
    else:
        print("\n❌ GROQ INTEGRATION TEST FAILED!")
        print("🔧 Please fix the configuration and try again")
