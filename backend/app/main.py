"""
PYTHON AI BACKEND - MLN131 CHATBOT - CHƯƠNG 03
Sử dụng FastAPI để tạo REST API cho AI chatbot
Tích hợp RAG (Retrieval-Augmented Generation) với Gemini AI
Tập trung vào nội dung Chương 03: Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội
"""

# Import các thư viện cần thiết
from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .services.enhanced_rag_service import EnhancedRAGService
from .services.quiz_service import QuizService
import google.generativeai as genai
import json
import requests

# Import utility for safe printing (handles Windows encoding)
from .utils import safe_print, setup_utf8_encoding

# Setup UTF-8 encoding for Windows console
setup_utf8_encoding()

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("Warning: Cannot find GEMINI_API_KEY — please check .env file or environment variables.")


# ===== KHỞI TẠO FASTAPI APPLICATION =====
app = FastAPI(title="MLN131 Chatbot - Chương 03 API", version="2.0.0")

# ===== CẤU HÌNH CORS =====
# Cho phép .NET API (localhost:9000) gọi Python API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả HTTP methods
    allow_headers=["*"],  # Cho phép tất cả headers
)

# ===== KHỞI TẠO AI SERVICE =====
# Enhanced RAG service - kết hợp tìm kiếm tri thức và tạo văn bản
rag_service = EnhancedRAGService()
quiz_service = QuizService()

# ===== DATA MODELS CHO API =====

class QuestionRequest(BaseModel):
    """Model cho request từ .NET API"""
    question: str  # Câu hỏi từ người dùng

class EnhancedChatResponse(BaseModel):
    """Model cho response trả về .NET API"""
    answer: str  # Câu trả lời từ AI
    confidence: int = 0  # Độ tin cậy (0-100)
    last_updated: str = None  # Thời gian cập nhật knowledge base

# ===== QUIZ MODELS =====
class QuizGenerateRequest(BaseModel):
    chapter: str = "Tất cả"
    num_questions: int = 10
    difficulty: str = "medium"

class ImageSearchRequest(BaseModel):
    query: str
    num_results: int = 10

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    username: str
    answers: Dict[str, str]  # {question_id: selected_answer}

class QuizResultResponse(BaseModel):
    """Response kết quả bài làm"""
    score: float
    correct_count: int
    total_questions: int
    percentage: float
    details: List[Dict[str, Any]]

# ===== LIFECYCLE EVENTS =====

async def background_load_knowledge_base():
    """Load knowledge base in the background without blocking startup"""
    try:
        print("Loading knowledge base in background...")
        rag_service.update_knowledge_base(force_update=True)
        print("Knowledge base loaded successfully!")
    except Exception as e:
        print(f"Warning: RAG service init failed: {e}")

@app.on_event("startup")
async def startup_event():
    """
    Khởi tạo knowledge base khi server start
    Tải và xử lý tất cả tài liệu về Chủ nghĩa xã hội và thời kỳ quá độ
    """
    print("Starting MLN131 Chatbot API...")
    print("Available endpoints:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"  {list(route.methods)} {route.path}")
    
    # Load knowledge base in background to speed up startup
    import asyncio
    asyncio.create_task(background_load_knowledge_base())
    print("Server ready! Knowledge base loading in background...")

# ===== API ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint - thông tin cơ bản về API"""
    return {"message": "MLN131 Chatbot - Chương 03 API", "version": "2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint - kiểm tra tình trạng AI service"""
    try:
        stats = rag_service.get_stats()
    except:
        # If stats fail, still return healthy (knowledge base might still be loading)
        stats = {"status": "initializing"}
    return {"status": "healthy", "stats": stats}

# ===== ADMIN ENDPOINTS =====
@app.post("/admin/reindex")
async def admin_reindex():
    """Re-index lại toàn bộ tài liệu .md trong thư mục book/ (xóa index cũ trước)."""
    try:
        rag_service.update_knowledge_base(force_update=True)
        return {"status": "ok", "stats": rag_service.get_stats()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindex lỗi: {e}")

@app.get("/admin/stats")
async def admin_stats():
    return rag_service.get_stats()

@app.post("/chat", response_model=EnhancedChatResponse)
async def enhanced_chat(request: QuestionRequest):
    """
    MAIN CHAT ENDPOINT - Xử lý câu hỏi và trả về phản hồi AI

    Quy trình:
    1. Validate input
    2. Sử dụng RAG service để tìm kiếm tri thức và tạo câu trả lời
    3. Nếu RAG thất bại, fallback về Gemini trực tiếp
    4. Trả về response với sources và confidence score
    """
    try:
        # ===== VALIDATION =====
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

        # ===== XỬ LÝ VỚI RAG SERVICE =====
        try:
            # Sử dụng Enhanced RAG để tạo response với nguồn tham khảo
            result = rag_service.generate_response_with_sources(request.question)

            return EnhancedChatResponse(
                answer=result["answer"],  # Câu trả lời chi tiết
                sources=result["sources"],  # Nguồn tham khảo có cấu trúc
                confidence=result["confidence"],  # Độ tin cậy
                last_updated=result.get("last_updated", "2024-01-01")
            )

        except Exception as rag_error:
            print(f"RAG service error: {rag_error}")

            # ===== FALLBACK: SỬ DỤNG GEMINI TRỰC TIẾP =====
            # Khi RAG service gặp lỗi (thường do quota API), dùng Gemini trực tiếp
            import google.generativeai as genai
            import os

            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-2.5-pro')

            # Prompt template cho fallback response
            prompt = f"""
            Câu hỏi về Chủ nghĩa xã hội và thời kỳ quá độ: {request.question}

            Hãy trả lời dựa trên kiến thức về Chủ nghĩa xã hội và thời kỳ quá độ, bao gồm:
            - Khái niệm chủ nghĩa xã hội
            - Thời kỳ quá độ lên chủ nghĩa xã hội
            - Đặc trưng bản chất của chủ nghĩa xã hội
            - Điều kiện ra đời của chủ nghĩa xã hội
            - Vận dụng ở Việt Nam
            """

            response = model.generate_content(prompt)

            return EnhancedChatResponse(
                answer=response.text,
                sources=["Kiến thức chung về Chủ nghĩa xã hội và thời kỳ quá độ"],  # Nguồn generic
                confidence=75,  # Độ tin cậy thấp hơn vì không có RAG
                last_updated="2024-01-01"
            )

    except Exception as e:
        print(f"Error in enhanced chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Lỗi server, vui lòng thử lại")

# ===== BOOK ENDPOINTS =====
BOOK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "book"))

def _slug_to_title(slug: str) -> str:
    s = slug.lower()
    mapping = {
        'tu-tuong-ho-chi-minh': 'Chủ nghĩa xã hội và thời kỳ quá độ',
        'muc-luc': 'Mục lục',
        'chuong1': 'Chương I',
        'chuong2': 'Chương II',
        'chuong3': 'Chương III',
        'chuong4': 'Chương IV',
        'chuong5': 'Chương V',
        'chuong6': 'Chương VI',
        'chuong-1': 'Chương I',
        'chuong-2': 'Chương II',
        'chuong-3': 'Chương III',
        'chuong-4': 'Chương IV',
        'chuong-5': 'Chương V',
        'chuong-6': 'Chương VI',
    }
    if s in mapping:
        return mapping[s]
    name = slug.replace('-', ' ').title()
    return name

@app.get("/book/list")
async def list_book_pages():
    try:
        if not os.path.exists(BOOK_DIR):
            return []
        items: List[dict] = []
        for fn in os.listdir(BOOK_DIR):
            if not fn.lower().endswith('.md'):
                continue
            slug = os.path.splitext(fn)[0]
            items.append({
                "slug": slug,
                "title": _slug_to_title(slug)
            })
        # Ưu tiên sắp xếp: tu-tuong-ho-chi-minh, muc-luc, chuong1..n, còn lại theo tên
        def sort_key(x):
            s = x['slug'].lower()
            if s == 'tu-tuong-ho-chi-minh':
                return '00'
            if s == 'muc-luc':
                return '01'
            if s.startswith('chuong'):
                num = ''.join(ch for ch in s if ch.isdigit())
                if num:
                    try:
                        return f"02{int(num):02d}"
                    except Exception:
                        pass
            return '10' + x['title']
        items.sort(key=sort_key)
        return items
    except Exception as e:
        print(f"Book list error: {e}")
        raise HTTPException(status_code=500, detail="Không đọc được danh sách trang sách")

@app.get("/book/content/{slug}")
async def get_book_content(slug: str):
    try:
        fp = os.path.join(BOOK_DIR, f"{slug}.md")
        if not os.path.exists(fp):
            raise HTTPException(status_code=404, detail="Không tìm thấy trang sách")
        with open(fp, 'r', encoding='utf-8') as f:
            md = f.read()
        return {
            "slug": slug,
            "title": _slug_to_title(slug),
            "markdown": md
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Book content error: {e}")
        raise HTTPException(status_code=500, detail="Không đọc được nội dung trang sách")

# ===== QUIZ ENDPOINTS =====

@app.post("/quiz/generate")
async def generate_quiz(request: QuizGenerateRequest):
    """Tạo bộ câu hỏi tự động dựa trên chương"""
    print(f"Received quiz generate request: {request.chapter}, {request.num_questions} questions")
    try:
        print("Step 1: Checking API key...")
        # Cấu hình Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: API key not found!")
            raise HTTPException(status_code=500, detail="Thiếu GEMINI_API_KEY")
        
        print("Step 2: Configuring Gemini...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        print("Step 3: Generating prompt...")
        
        # Prompt để tạo câu hỏi
        prompt = f"""
        Tạo {request.num_questions} câu hỏi trắc nghiệm về Chủ nghĩa xã hội và thời kỳ quá độ {request.chapter}.
        Độ khó: {request.difficulty}
        
        Yêu cầu:
        1. Mỗi câu hỏi có 4 đáp án A, B, C, D
        2. Chỉ có 1 đáp án đúng
        3. Câu hỏi phải rõ ràng, chính xác về mặt lý luận
        4. Kèm giải thích ngắn gọn cho đáp án đúng
        
        Trả về JSON với format:
        {{
            "questions": [
                {{
                    "id": "q1",
                    "question": "Câu hỏi...",
                    "options": {{
                        "A": "Đáp án A",
                        "B": "Đáp án B", 
                        "C": "Đáp án C",
                        "D": "Đáp án D"
                    }},
                    "correct_answer": "A",
                    "explanation": "Giải thích..."
                }}
            ]
        }}
        
        CHỈ TRẢ VỀ JSON, KHÔNG CÓ TEXT KHÁC.
        """
        
        print("Step 4: Calling Gemini API...")
        response = model.generate_content(prompt)
        print("Step 5: Getting response text...")
        response_text = response.text
        print(f"Response length: {len(response_text)} chars")
        
        # Xử lý để lấy JSON
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        print("Step 6: Parsing JSON...")
        # Parse JSON
        quiz_data = json.loads(response_text.strip())
        
        print("Step 7: Adding metadata...")
        # Thêm metadata
        quiz_data['title'] = f"Bài kiểm tra {request.chapter}"
        quiz_data['chapter'] = request.chapter
        quiz_data['difficulty'] = request.difficulty
        quiz_data['num_questions'] = request.num_questions
        
        print("Step 8: Saving quiz...")
        # Lưu quiz
        quiz_id = quiz_service.save_quiz(quiz_data)
        quiz_data['id'] = quiz_id
        
        print(f"SUCCESS: Quiz created successfully with ID: {quiz_id}")
        return quiz_data
        
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON Parse Error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi parse JSON từ AI: {str(e)}")
    except Exception as e:
        print(f"ERROR: General Error: {e}")
        print(f"ERROR: Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi tạo câu hỏi: {str(e)}")

# ===== IMAGE SEARCH ENDPOINTS =====

@app.post("/images/search")
async def search_images(request: ImageSearchRequest):
    """Tìm ảnh - DISABLED để tránh external API calls"""
    print(f" Image search request DISABLED: query='{request.query}', num_results={request.num_results}")
    
    # Return empty results to prevent external API calls
    return {
        "images": [],
        "total_results": 0,
        "message": "Image search disabled to prevent external API calls"
    }
    
    # DISABLED CODE BELOW - External API calls removed
    """
    try:
        print("Step 1: Checking API keys...")
        api_key = os.getenv("GOOGLE_CSE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        
        print(f" API Key: {api_key[:20]}..." if api_key else "ERROR: No API Key")
        print(f" CSE ID: {cse_id}")
        
        if not api_key or not cse_id:
            print("ERROR: Missing Google CSE configuration")
            raise HTTPException(status_code=500, detail="Thiếu cấu hình Google CSE")
        
        print("Step 2: Preparing Google CSE request...")
        # Gọi Google Custom Search API
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': f"Chủ nghĩa xã hội {request.query}",
            'searchType': 'image',
            'num': min(request.num_results, 10),
            'safe': 'active',
            'imgType': 'photo'
        }
        
        print(f"Step 3: Calling Google CSE API with params: {params}")
        response = requests.get(url, params=params)
        print(f"Step 4: Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"ERROR: Google CSE API error: {response.text}")
            raise HTTPException(status_code=500, detail=f"Lỗi gọi Google CSE API: {response.status_code}")
        
        print("Step 5: Parsing response...")
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        print(f"Total results info: {data.get('searchInformation', {})}")
        
        images = []
        items = data.get('items', [])
        print(f"Found {len(items)} items")
        
        for i, item in enumerate(items):
            print(f"Processing item {i+1}: {item.get('title', 'No title')}")
            images.append({
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'thumbnail': item.get('image', {}).get('thumbnailLink', ''),
                'original': item.get('link', ''),
                'source': item.get('displayLink', ''),
                'context': item.get('image', {}).get('contextLink', '')
            })
        
        print(f"SUCCESS: Successfully processed {len(images)} images")
        return {
            'query': request.query,
            'total': len(images),
            'images': images
        }
        
    except Exception as e:
        print(f"ERROR: Image search error: {e}")
        print(f"ERROR: Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi tìm ảnh: {str(e)}")
    """

@app.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Lấy nội dung quiz"""
    quiz_data = quiz_service.get_quiz(quiz_id)
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài kiểm tra")
    return quiz_data

@app.post("/quiz/submit", response_model=QuizResultResponse)
async def submit_quiz(request: QuizSubmitRequest):
    """Nộp bài và tính điểm"""
    try:
        # Lấy quiz data
        quiz_data = quiz_service.get_quiz(request.quiz_id)
        if not quiz_data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài kiểm tra")
        
        # Tính điểm
        result = quiz_service.calculate_score(quiz_data, request.answers)
        
        # Lưu kết quả
        result_data = {
            **result,
            'quiz_title': quiz_data.get('title', ''),
            'quiz_chapter': quiz_data.get('chapter', '')
        }
        
        result_id = quiz_service.save_quiz_result(
            request.username,
            request.quiz_id,
            result_data
        )
        
        result['result_id'] = result_id
        return QuizResultResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý bài làm: {str(e)}")

@app.get("/quiz/history/{username}")
async def get_quiz_history(username: str, limit: Optional[int] = 10):
    """Lấy lịch sử làm bài của user"""
    try:
        results = quiz_service.get_user_results(username, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy lịch sử: {str(e)}")

@app.get("/quiz/result/{username}/{result_id}")
async def get_quiz_result(username: str, result_id: str):
    """Xem chi tiết kết quả bài làm"""
    result = quiz_service.get_result_detail(username, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả")
    return result

# ===== SERVER ENTRY POINT =====
if __name__ == "__main__":
    """
    Chạy server trực tiếp (cho development và production)
    Port sẽ được lấy từ environment variable PORT hoặc mặc định 8000
    """
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
