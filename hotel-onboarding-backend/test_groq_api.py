#!/usr/bin/env python3
"""Test Groq API connection and available models"""

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

def test_groq_connection():
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return
    
    print(f"🔑 Using API key: {api_key[:10]}...")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Try to list models
        print("\n📋 Attempting to list available models...")
        models = client.models.list()
        
        print(f"\n✅ Successfully connected to Groq API!")
        print(f"Found {len(models.data)} models:\n")
        
        # Categorize models
        vision_models = []
        text_models = []
        
        for model in models.data:
            model_id = model.id
            print(f"  - {model_id}")
            
            # Check for vision models
            if any(keyword in model_id.lower() for keyword in ['vision', 'scout', 'maverick', 'llava', 'image']):
                vision_models.append(model_id)
            else:
                text_models.append(model_id)
        
        print(f"\n🖼️  Vision/Multimodal Models ({len(vision_models)}):")
        for model in vision_models:
            print(f"  - {model}")
            
        print(f"\n📝 Text Models ({len(text_models)}):")
        for model in text_models[:5]:  # Show first 5 text models
            print(f"  - {model}")
        if len(text_models) > 5:
            print(f"  ... and {len(text_models) - 5} more")
            
        # Test a simple completion with a text model
        print("\n🧪 Testing simple text completion...")
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Use a simple text model
                messages=[
                    {"role": "user", "content": "Say 'Hello from Groq!' in 5 words or less"}
                ],
                temperature=0.5,
                max_tokens=50
            )
            print(f"✅ Test completion successful: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"⚠️  Text completion failed: {str(e)}")
            
    except Exception as e:
        print(f"\n❌ Failed to connect to Groq API")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        if "403" in str(e):
            print("\n🔐 This appears to be an authentication issue. Possible causes:")
            print("  1. Invalid or expired API key")
            print("  2. API key doesn't have necessary permissions")
            print("  3. Account restrictions or rate limits")
            print("  4. IP address restrictions on the API key")
            print("\n💡 Try generating a new API key at: https://console.groq.com/keys")
        elif "404" in str(e):
            print("\n🔍 Model not found. The model name might have changed.")
        else:
            print("\n💡 Check your internet connection and firewall settings")

if __name__ == "__main__":
    test_groq_connection()