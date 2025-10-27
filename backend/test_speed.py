#!/usr/bin/env python3
"""
Script test tốc độ response của AI backend
"""
import time
import requests
import json

def test_chat_speed():
    """Test tốc độ response của chat API"""
    url = "http://localhost:8000/chat"
    
    test_questions = [
        "Chủ nghĩa xã hội là gì?",
        "Thời kỳ quá độ lên chủ nghĩa xã hội có đặc điểm gì?",
        "Điều kiện ra đời của chủ nghĩa xã hội?",
        "Các đặc trưng bản chất của chủ nghĩa xã hội?",
        "Vai trò của Đảng Cộng sản trong thời kỳ quá độ?"
    ]
    
    print("🚀 Testing AI Response Speed...")
    print("=" * 50)
    
    total_time = 0
    successful_requests = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/5: {question}")
        
        payload = {
            "question": question,
            "username": "test_user"
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=30)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            successful_requests += 1
            
            if response.status_code == 200:
                data = response.json()
                answer_length = len(data.get('answer', ''))
                print(f"✅ Success: {response_time:.2f}s | Answer length: {answer_length} chars")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout after 30s")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if successful_requests > 0:
        avg_time = total_time / successful_requests
        print(f"\n📊 RESULTS:")
        print(f"   Successful requests: {successful_requests}/5")
        print(f"   Average response time: {avg_time:.2f}s")
        print(f"   Total time: {total_time:.2f}s")
        
        if avg_time < 3:
            print("🟢 Speed: EXCELLENT (< 3s)")
        elif avg_time < 5:
            print("🟡 Speed: GOOD (3-5s)")
        elif avg_time < 10:
            print("🟠 Speed: ACCEPTABLE (5-10s)")
        else:
            print("🔴 Speed: SLOW (> 10s)")
    else:
        print("❌ No successful requests")

if __name__ == "__main__":
    test_chat_speed()
