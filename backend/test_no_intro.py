#!/usr/bin/env python3
"""
Test để xác nhận chatbot không còn bắt đầu bằng "Với tư cách là..."
"""
import requests
import json
import time

def test_no_intro():
    url = "http://localhost:8000/chat"
    
    # Đợi backend khởi động
    print("⏳ Đợi backend khởi động...")
    time.sleep(10)
    
    payload = {
        "question": "Chủ nghĩa xã hội là gì?",
        "username": "test_user"
    }
    
    print("\n🧪 Testing - No Introduction...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            
            print(f"✅ Status: {response.status_code}")
            print(f"📝 Answer length: {len(answer)} chars")
            
            # Kiểm tra các cụm từ không mong muốn
            bad_phrases = [
                "Với tư cách là",
                "với tư cách là",
                "Tôi là chuyên gia",
                "tôi là chuyên gia",
                "chuyên gia về tư tưởng Hồ Chí Minh",
                "Chuyên gia về tư tưởng Hồ Chí Minh"
            ]
            
            found_bad = False
            for phrase in bad_phrases:
                if phrase in answer:
                    print(f"🔴 FOUND BAD PHRASE: '{phrase}'")
                    found_bad = True
                    break
            
            if not found_bad:
                print(f"🟢 NO BAD PHRASES FOUND!")
            
            # Hiển thị preview
            print(f"\n💬 ANSWER PREVIEW (first 500 chars):")
            print("-" * 60)
            print(answer[:500])
            print("-" * 60)
            
            if not found_bad:
                print(f"\n🎉 SUCCESS: Chatbot trả lời trực tiếp, không tự giới thiệu!")
            else:
                print(f"\n🔴 ISSUE: Chatbot vẫn tự giới thiệu")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_no_intro()
