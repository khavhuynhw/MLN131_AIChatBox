#!/usr/bin/env python3
"""
Simple test để kiểm tra chatbot
"""
import requests
import json

def simple_test():
    url = "http://localhost:8000/chat"
    
    payload = {
        "question": "Chủ nghĩa xã hội là gì?",
        "username": "test_user"
    }
    
    print("🧪 Testing simple question...")
    print(f"Question: {payload['question']}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            sources = data.get('sources', [])
            
            print(f"✅ Success!")
            print(f"Answer length: {len(answer)}")
            print(f"Sources count: {len(sources)}")
            
            # Check sources
            chapter03_count = 0
            for source in sources:
                doc = source.get('document', '')
                if 'Chương III' in doc:
                    chapter03_count += 1
                    print(f"  📖 Chapter 03 source: {doc}")
            
            print(f"Chapter 03 sources: {chapter03_count}/{len(sources)}")
            
            if answer:
                print(f"Answer preview: {answer[:200]}...")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    simple_test()
