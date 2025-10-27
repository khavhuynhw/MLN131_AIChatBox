#!/usr/bin/env python3
"""
Script test để xác nhận chatbot chỉ sử dụng dữ liệu từ Chương 03
"""
import requests
import json

def test_chapter03_only():
    """Test xem chatbot có chỉ trả lời dựa trên Chương 03 không"""
    url = "http://localhost:8000/chat"
    
    # Test questions về các chương khác (không nên có trong Chương 03)
    test_questions = [
        {
            "question": "Tư tưởng Hồ Chí Minh về đạo đức là gì?",
            "expected": "should_not_know",  # Không có trong Chương 03
            "description": "Câu hỏi về tư tưởng Hồ Chí Minh (không có trong Chương 03)"
        },
        {
            "question": "Chủ nghĩa xã hội là gì?",
            "expected": "should_know",  # Có trong Chương 03
            "description": "Câu hỏi về chủ nghĩa xã hội (có trong Chương 03)"
        },
        {
            "question": "Thời kỳ quá độ lên chủ nghĩa xã hội có đặc điểm gì?",
            "expected": "should_know",  # Có trong Chương 03
            "description": "Câu hỏi về thời kỳ quá độ (có trong Chương 03)"
        },
        {
            "question": "Điều kiện ra đời của chủ nghĩa xã hội?",
            "expected": "should_know",  # Có trong Chương 03
            "description": "Câu hỏi về điều kiện ra đời (có trong Chương 03)"
        },
        {
            "question": "Vai trò của Đảng Cộng sản Việt Nam trong thời kỳ quá độ?",
            "expected": "should_know",  # Có trong Chương 03
            "description": "Câu hỏi về vai trò Đảng (có trong Chương 03)"
        }
    ]
    
    print("🧪 Testing Chapter 03 Only Content...")
    print("=" * 60)
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/5: {test['description']}")
        print(f"   Question: {test['question']}")
        
        payload = {
            "question": test['question'],
            "username": "test_user"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                sources = data.get('sources', [])
                
                # Kiểm tra nguồn trích dẫn
                chapter03_sources = 0
                for source in sources:
                    if 'Chương III' in source.get('document', ''):
                        chapter03_sources += 1
                
                print(f"   ✅ Response received")
                print(f"   📊 Sources from Chapter 03: {chapter03_sources}/{len(sources)}")
                print(f"   📝 Answer length: {len(answer)} chars")
                
                # Đánh giá kết quả
                if test['expected'] == 'should_know':
                    if chapter03_sources > 0:
                        print(f"   🟢 CORRECT: Found Chapter 03 sources")
                    else:
                        print(f"   🟡 WARNING: No Chapter 03 sources found")
                else:
                    if chapter03_sources == 0:
                        print(f"   🟢 CORRECT: No Chapter 03 sources (as expected)")
                    else:
                        print(f"   🔴 ERROR: Found Chapter 03 sources (should not have)")
                
                # Hiển thị preview answer
                if answer:
                    preview = answer[:100] + "..." if len(answer) > 100 else answer
                    print(f"   💬 Answer preview: {preview}")
                    
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 15s")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ If all tests show Chapter 03 sources for relevant questions")
    print(f"   ✅ And no Chapter 03 sources for irrelevant questions")
    print(f"   ✅ Then the system is correctly using only Chapter 03 data!")

if __name__ == "__main__":
    test_chapter03_only()
