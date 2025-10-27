#!/usr/bin/env python3
"""
Script test để xác nhận chatbot không còn tham chiếu đến "tư tưởng Hồ Chí Minh"
"""
import requests
import json

def test_no_hcm_reference():
    """Test xem chatbot có còn tham chiếu đến HCM không"""
    url = "http://localhost:8000/chat"
    
    test_questions = [
        "Chủ nghĩa xã hội là gì?",
        "Thời kỳ quá độ lên chủ nghĩa xã hội có đặc điểm gì?",
        "Điều kiện ra đời của chủ nghĩa xã hội?",
        "Các đặc trưng bản chất của chủ nghĩa xã hội?",
        "Vai trò của Đảng Cộng sản Việt Nam trong thời kỳ quá độ?"
    ]
    
    print("🧪 Testing No HCM Reference...")
    print("=" * 50)
    
    hcm_references_found = 0
    total_tests = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/5: {question}")
        
        payload = {
            "question": question,
            "username": "test_user"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                sources = data.get('sources', [])
                
                print(f"   ✅ Response received")
                print(f"   📝 Answer length: {len(answer)} chars")
                print(f"   📊 Sources count: {len(sources)}")
                
                # Kiểm tra tham chiếu HCM
                hcm_keywords = [
                    "tư tưởng Hồ Chí Minh",
                    "HCM",
                    "Hồ Chí Minh",
                    "tư tưởng HCM",
                    "tư tưởng của Hồ Chí Minh"
                ]
                
                found_hcm = False
                for keyword in hcm_keywords:
                    if keyword.lower() in answer.lower():
                        print(f"   🔴 FOUND HCM REFERENCE: '{keyword}'")
                        found_hcm = True
                        hcm_references_found += 1
                        break
                
                if not found_hcm:
                    print(f"   🟢 NO HCM REFERENCES FOUND")
                
                # Kiểm tra nguồn trích dẫn
                chapter03_sources = 0
                for source in sources:
                    if 'Chương III' in source.get('document', ''):
                        chapter03_sources += 1
                
                print(f"   📖 Chapter 03 sources: {chapter03_sources}/{len(sources)}")
                
                # Hiển thị preview answer
                if answer:
                    preview = answer[:150] + "..." if len(answer) > 150 else answer
                    print(f"   💬 Answer preview: {preview}")
                    
                total_tests += 1
                    
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 20s")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Total tests: {total_tests}")
    print(f"   HCM references found: {hcm_references_found}")
    
    if hcm_references_found == 0:
        print(f"   🟢 SUCCESS: No HCM references found!")
        print(f"   ✅ Chatbot is now focused on Chapter 03 only!")
    else:
        print(f"   🔴 ISSUE: Still found {hcm_references_found} HCM references")
        print(f"   ⚠️  Need to fix remaining HCM references")

if __name__ == "__main__":
    test_no_hcm_reference()
