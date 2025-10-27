#!/usr/bin/env python3
"""
Test cuối cùng để xác nhận chatbot đã được sửa hoàn toàn
"""
import requests
import json
import time

def test_final_fix():
    url = "http://localhost:8000/chat"
    
    # Đợi backend khởi động
    print("⏳ Đợi backend khởi động...")
    time.sleep(10)
    
    payload = {
        "question": "Chủ nghĩa xã hội là gì?",
        "username": "test_user"
    }
    
    print("\n🧪 Final Test - Complete Fix...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            sources = data.get('sources', [])
            
            print(f"✅ Status: {response.status_code}")
            print(f"📝 Answer length: {len(answer)} chars")
            print(f"📊 Sources count: {len(sources)}")
            
            # Kiểm tra các cụm từ không mong muốn
            bad_phrases = [
                "Với tư cách là",
                "với tư cách là",
                "Tôi là chuyên gia",
                "tôi là chuyên gia",
                "chuyên gia về tư tưởng Hồ Chí Minh",
                "Chuyên gia về tư tưởng Hồ Chí Minh",
                "là một chuyên gia về tư tưởng Hồ Chí Minh",
                "Chào bạn, là một chuyên gia"
            ]
            
            found_bad = False
            for phrase in bad_phrases:
                if phrase in answer:
                    print(f"🔴 FOUND BAD PHRASE: '{phrase}'")
                    found_bad = True
                    break
            
            if not found_bad:
                print(f"🟢 NO BAD PHRASES FOUND!")
            
            # Kiểm tra nguồn trích dẫn
            chapter03_sources = 0
            for source in sources:
                if 'Chương III' in source.get('document', ''):
                    chapter03_sources += 1
            
            print(f"📖 Chapter 03 sources: {chapter03_sources}/{len(sources)}")
            
            # Hiển thị answer
            print(f"\n💬 ANSWER:")
            print("-" * 60)
            print(answer[:800])
            print("-" * 60)
            
            if not found_bad and chapter03_sources > 0:
                print(f"\n🎉 SUCCESS: Chatbot hoàn toàn sạch và chỉ dùng Chương 03!")
            elif not found_bad:
                print(f"\n🟡 PARTIAL SUCCESS: Không có cụm từ xấu, nhưng cần kiểm tra sources")
            else:
                print(f"\n🔴 ISSUE: Vẫn còn cụm từ không mong muốn")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_final_fix()
