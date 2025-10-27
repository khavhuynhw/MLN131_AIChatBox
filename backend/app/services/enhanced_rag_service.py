import google.generativeai as genai
from .vector_store import SimpleVectorStore
# from .web_data_collector import WebDataCollector  # Disabled to prevent external API calls
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from typing import List
from urllib.parse import quote
import unicodedata
import re

load_dotenv()

class EnhancedRAGService:
    def __init__(self):
        self.vector_store = SimpleVectorStore()
        # self.data_collector = WebDataCollector()  # Disabled to prevent external API calls
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.last_update = None
        print("Enhanced RAG Service v2.1 ready with improved citations!")
    
    def add_chapter03_corpus(self):
        """Thêm corpus Chương 03: Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội"""
        # Load Chapter 03 content from file
        chapter03_path = os.path.join(os.path.dirname(__file__), "../../data/book/chuong3.md")
        
        if not os.path.exists(chapter03_path):
            print(f"⚠️ Không tìm thấy file {chapter03_path}")
            return
        
        with open(chapter03_path, 'r', encoding='utf-8') as f:
            chapter03_content = f.read()
        
        # Split content into meaningful chunks
        comprehensive_docs = self._split_chapter03_content(chapter03_content)
        
        # Create metadata for Chapter 03 content
        comprehensive_metadata = []
        for i, doc in enumerate(comprehensive_docs):
            metadata = {
                "source": "Giáo trình Chủ nghĩa xã hội khoa học (K-2021)",
                "document": "Chương III: Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội",
                "topic": "chủ nghĩa xã hội",
                "page": f"chunk_{i+1}",
                "credibility_score": 100,
                "source_type": "textbook"
            }
            comprehensive_metadata.append(metadata)
        
        self.vector_store.add_documents(comprehensive_docs, comprehensive_metadata)
        print(f"Added {len(comprehensive_docs)} documents from Chapter 03 with detailed citations")
    
    def _split_chapter03_content(self, content: str) -> List[str]:
        """Chia nội dung Chương 03 thành các đoạn có ý nghĩa"""
        # Split by major sections
        sections = re.split(r'\n(?=[IVX]+\.)', content)
        
        chunks = []
        for section in sections:
            if not section.strip():
                continue
                
            # Further split by paragraphs
            paragraphs = section.split('\n\n')
            current_chunk = ""
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                    
                # If adding this paragraph would make chunk too long, save current chunk
                if len(current_chunk) + len(paragraph) > 1000 and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # Add remaining chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
        
        return chunks

    def load_chapter03_data(self):
        """Load dữ liệu Chương 03 vào vector store"""
        print("🔄 Đang tải dữ liệu Chương 03...")
        self.add_chapter03_corpus()
        print("✅ Hoàn thành tải dữ liệu Chương 03!")

    def ingest_markdown_folder(self, folder_path: str):
        """Đọc tất cả các file .md trong thư mục và đưa vào vector store.
        - Mọi citation sẽ trỏ về 'Giáo trình Chủ nghĩa xã hội khoa học'.
        - 'document' là tên file (không đuôi), ví dụ: 'chuong3' -> 'Chương 03'.
        """
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                print(f"Tạo thư mục book: {folder_path}")

            md_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.md')]
            if not md_files:
                print(f"Không tìm thấy file .md trong {folder_path}")
                return

            all_docs, all_metas = [], []
            for fname in md_files:
                fpath = os.path.join(folder_path, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if not content:
                        continue

                    # Cắt nhỏ nội dung để index
                    chunks = self.split_text(content, max_length=700)
                    # Tên hiển thị của tài liệu
                    base = os.path.splitext(fname)[0]
                    display_name = base.replace('-', ' ').title()
                    # Chuẩn hóa tên hiển thị với dấu tiếng Việt cho các trang chính
                    bl = base.lower()
                    if bl == 'tu-tuong-ho-chi-minh':
                        display_name = 'Chủ nghĩa xã hội và thời kỳ quá độ'
                    elif bl == 'muc-luc':
                        display_name = 'Mục lục'
                    elif bl in ('chuong1', 'chuong-1'):
                        display_name = 'Chương I'
                    elif bl in ('chuong2', 'chuong-2'):
                        display_name = 'Chương II'
                    elif bl in ('chuong3', 'chuong-3'):
                        display_name = 'Chương III'
                    elif bl in ('chuong4', 'chuong-4'):
                        display_name = 'Chương IV'
                    elif bl in ('chuong5', 'chuong-5'):
                        display_name = 'Chương V'
                    elif bl in ('chuong6', 'chuong-6'):
                        display_name = 'Chương VI'

                    for ch in chunks:
                        all_docs.append(ch)
                        all_metas.append({
                            "source": "Giáo trình Chủ nghĩa xã hội khoa học (K-2021)",
                            "document": display_name,
                            "page": base,
                            "credibility_score": 95,
                            "source_type": "document",
                            "url": f"/book/{base}"
                        })
                except Exception as e:
                    print(f"Error reading {fname}: {e}")

            if all_docs:
                self.vector_store.add_documents(all_docs, all_metas)
                print(f"Ingested {len(all_docs)} segments from markdown folder {folder_path}")
        except Exception as e:
            print(f"Error ingesting markdown: {e}")
    
    def update_knowledge_base(self, force_update=False):
        """Cập nhật knowledge base chỉ từ Chương 03: Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội.
        Nếu force_update=True: xóa index cũ trước khi ingest để tránh lẫn nguồn cũ.
        """
        if force_update:
            self.vector_store.reset()
        self.load_chapter03_data()
        self.last_update = datetime.now()
        print("Knowledge base updated từ Chương 03: Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội")
    
    def split_text(self, text: str, max_length: int = 700) -> List[str]:
        """Chia nhỏ theo đoạn (paragraph-first) để giữ nguyên các khối định nghĩa/trích dẫn.
        - Ưu tiên tách theo 2+ dòng trắng.
        - Nếu đoạn quá dài, fallback tách theo câu '. '.
        """
        paras = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
        chunks: List[str] = []
        for p in paras:
            if len(p) <= max_length:
                chunks.append(p)
            else:
                sentences = p.split('. ')
                current = ""
                for s in sentences:
                    if len(current) + len(s) + 2 <= max_length:
                        current += (s + ". ")
                    else:
                        if current:
                            chunks.append(current.strip())
                        current = s + ". "
                if current:
                    chunks.append(current.strip())
        return chunks
    
    def _normalize(self, s: str) -> str:
        """Chuẩn hóa text: loại bỏ dấu tiếng Việt và chuyển thành chữ thường"""
        if not s:
            return ''
        
        # Bảng chuyển đổi ký tự có dấu tiếng Việt
        vietnamese_chars = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'đ': 'd', 'Đ': 'd'
        }
        
        # Chuyển thành chữ thường
        s = s.lower()
        
        # Thay thế các ký tự có dấu
        for vn_char, latin_char in vietnamese_chars.items():
            s = s.replace(vn_char, latin_char)
        
        # Loại bỏ các ký tự đặc biệt, chỉ giữ chữ và số
        s = re.sub(r'[^a-z0-9\s]', '', s)
        
        # Chuẩn hóa khoảng trắng
        s = re.sub(r'\s+', ' ', s).strip()
        
        return s

    def _slug_to_title(self, slug: str) -> str:
        s = (slug or '').lower().strip()
        mapping = {
            'chuong1': 'Chương I',
            'chuong2': 'Chương II',
            'chuong3': 'Chương III',
            'chuong4': 'Chương IV',
            'chuong5': 'Chương V',
            'chuong6': 'Chương VI',
        }
        return mapping.get(s, slug or '')
    
    def detect_chapter_summary_request(self, question: str) -> tuple[bool, str]:
        """Phát hiện yêu cầu tóm tắt chương và trả về (is_summary, chapter_name)"""
        q_norm = self._normalize(question)
        summary_keywords = ['tom tat', 'tom tac', 'tong ket', 'noi dung chinh', 'yeu to']
        chapter_keywords = ['chuong', 'phan']
        
        # Kiểm tra có từ khóa tóm tắt
        has_summary = any(kw in q_norm for kw in summary_keywords)
        has_chapter = any(kw in q_norm for kw in chapter_keywords)
        
        if not (has_summary and has_chapter):
            return False, ""
        
        # Tìm số chương
        import re
        # Tìm chương bằng số La Mã hoặc số Arabic
        chapter_match = re.search(r'chương\s*(\d+|[ivxlcdm]+)', q_norm)
        if chapter_match:
            chapter_num = chapter_match.group(1)
            # Chuyển số La Mã thành số Arabic nếu cần
            roman_to_num = {'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5', 'vi': '6'}
            if chapter_num.lower() in roman_to_num:
                chapter_num = roman_to_num[chapter_num.lower()]
            return True, f"chuong{chapter_num}"
        
        # Tìm theo pattern "chương X"
        for i in range(1, 7):
            if f"chuong {i}" in q_norm or f"chuong{i}" in q_norm:
                return True, f"chuong{i}"
        
        return False, ""
    
    def detect_mindmap_request(self, question: str) -> bool:
        """Phát hiện yêu cầu tạo sơ đồ tư duy"""
        q_norm = self._normalize(question)
        mindmap_keywords = [
            'tao so do tu duy',
            'so do tu duy',
            've so do',
            'so do ve',
            'bieu do',
            'so do',
            'mindmap',
            'mind map',
            'mermaid mindmap',
            'hien thi so do',
            'tao so do'
        ]
        
        is_mindmap = any(kw in q_norm for kw in mindmap_keywords)
        print(f"🔍 MINDMAP DEBUG: '{question}' -> normalized: '{q_norm}' -> is_mindmap: {is_mindmap}")
        return is_mindmap
    
    def detect_off_topic_question(self, question: str) -> bool:
        """Phát hiện câu hỏi không liên quan đến chủ nghĩa xã hội"""
        q_norm = self._normalize(question)
        
        # Các từ khóa liên quan đến chủ nghĩa xã hội
        socialism_keywords = [
            'chu nghia xa hoi', 'chủ nghĩa xã hội', 'cnxh', 'cnx',
            'thoi ky qua do', 'thời kỳ quá độ', 'qua do', 'quá độ',
            'mac lenin', 'mác lênin', 'mac', 'mác', 'lenin', 'lênin',
            'cong san', 'cộng sản', 'tu ban', 'tư bản', 'giai cap', 'giai cấp',
            'cach mang', 'cách mạng', 'vo san', 'vô sản', 'tu san', 'tư sản',
            'dang cong san', 'đảng cộng sản', 'nha nuoc', 'nhà nước',
            'kinh te', 'kinh tế', 'san xuat', 'sản xuất', 'quan he', 'quan hệ',
            'hinh thai', 'hình thái', 'xã hội', 'xa hoi', 'che do', 'chế độ',
            'dac trung', 'đặc trưng', 'ban chat', 'bản chất', 'muc tieu', 'mục tiêu',
            'phuong huong', 'phương hướng', 'xay dung', 'xây dựng', 'phat trien', 'phát triển'
        ]
        
        # Các từ khóa không liên quan
        off_topic_keywords = [
            'thoi tiet', 'thời tiết', 'weather', 'mua', 'mưa', 'nang', 'nắng',
            'am nhac', 'âm nhac', 'music', 'nhac', 'nhạc', 'bai hat', 'bài hát',
            'phim', 'movie', 'film', 'dien anh', 'điện ảnh', 'tv', 'tivi',
            'the thao', 'thể thao', 'sport', 'bong da', 'bóng đá', 'football',
            'game', 'tro choi', 'trò chơi', 'video game', 'game online',
            'du lich', 'du lịch', 'travel', 'di choi', 'đi chơi', 'nghi mat', 'nghỉ mát',
            'an uong', 'ăn uống', 'food', 'thuc an', 'thức ăn', 'mon an', 'món ăn',
            'nau an', 'nấu ăn', 'cach nau', 'cách nấu', 'pho', 'phở', 'bun', 'bún',
            'thoi trang', 'thời trang', 'fashion', 'quan ao', 'quần áo', 'giay dep', 'giày dép',
            'lam dep', 'làm đẹp', 'beauty', 'my pham', 'mỹ phẩm', 'trang diem', 'trang điểm',
            'cong nghe', 'công nghệ', 'technology', 'dien thoai', 'điện thoại', 'smartphone',
            'may tinh', 'máy tính', 'computer', 'laptop', 'internet', 'wifi',
            'hoc tap', 'học tập', 'study', 'hoc', 'học', 'bai tap', 'bài tập',
            'cong viec', 'công việc', 'job', 'viec lam', 'việc làm', 'tuyen dung', 'tuyển dụng',
            'tinh yeu', 'tình yêu', 'love', 'yeu', 'yêu', 'hen ho', 'hẹn hò',
            'gia dinh', 'gia đình', 'family', 'bo me', 'bố mẹ', 'cha me', 'cha mẹ',
            'ban be', 'bạn bè', 'friend', 'ban', 'bạn', 'tinh ban', 'tình bạn',
            'mua sam', 'mua sắm', 'shopping', 'mua', 'mua', 'ban', 'bán', 'gia', 'giá'
        ]
        
        # Các từ khóa cảm tính/đánh giá chủ quan
        emotional_keywords = [
            'tot hay khong', 'tốt hay không', 'hay hay khong', 'hay hay không',
            'co tot khong', 'có tốt không', 'tot nhat', 'tốt nhất', 'hay nhat', 'hay nhất',
            'danh gia', 'đánh giá', 'y kien', 'ý kiến', 'suy nghi', 'suy nghĩ',
            'cam nhan', 'cảm nhận', 'cam giac', 'cảm giác', 'thich', 'thích',
            'khong thich', 'không thích', 'ghet', 'ghét', 'yeu', 'yêu',
            'thuong', 'thương', 'ghe', 'ghê', 'kinh', 'kinh khủng',
            'tuyet voi', 'tuyệt vời', 'kinh khung', 'kinh khủng', 'toi te', 'tồi tệ',
            'xau', 'xấu', 'dep', 'đẹp', 'xinh', 'xinh đẹp', 'dep trai', 'đẹp trai',
            'thong minh', 'thông minh', 'ngu', 'ngu ngốc', 'stupid', 'smart',
            'good', 'bad', 'excellent', 'terrible', 'awesome', 'horrible'
        ]
        
        # Kiểm tra xem có từ khóa liên quan đến chủ nghĩa xã hội không
        has_socialism_keywords = any(keyword in q_norm for keyword in socialism_keywords)
        
        # Kiểm tra xem có từ khóa không liên quan không
        has_off_topic_keywords = any(keyword in q_norm for keyword in off_topic_keywords)
        
        # Kiểm tra xem có từ khóa cảm tính/đánh giá chủ quan không
        has_emotional_keywords = any(keyword in q_norm for keyword in emotional_keywords)
        
        # Nếu có từ khóa không liên quan và không có từ khóa liên quan đến CNXH
        is_off_topic = has_off_topic_keywords and not has_socialism_keywords
        
        # Nếu có từ khóa cảm tính (bất kể có từ khóa CNXH hay không)
        is_emotional = has_emotional_keywords
        
        # Kết hợp cả hai điều kiện
        is_inappropriate = is_off_topic or is_emotional
        
        print(f"🔍 OFF-TOPIC DEBUG: '{question}' -> normalized: '{q_norm}' -> is_off_topic: {is_off_topic}, is_emotional: {is_emotional}, is_inappropriate: {is_inappropriate}")
        return is_inappropriate
    
    def _handle_off_topic_question(self, question: str):
        """Xử lý câu hỏi không liên quan hoặc cảm tính về chủ nghĩa xã hội"""
        print(f"🚫 Handling off-topic/emotional question: {question}")
        
        # Kiểm tra xem có phải câu hỏi cảm tính không
        q_norm = self._normalize(question)
        emotional_keywords = [
            'tot hay khong', 'tốt hay không', 'hay hay khong', 'hay hay không',
            'co tot khong', 'có tốt không', 'danh gia', 'đánh giá', 'y kien', 'ý kiến'
        ]
        is_emotional = any(keyword in q_norm for keyword in emotional_keywords)
        
        if is_emotional:
            response = f"""Tôi hiểu bạn muốn đánh giá về chủ nghĩa xã hội, nhưng tôi là chatbot học thuật chuyên cung cấp **thông tin khách quan** về **Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội**.

### 🎯 Thay vì đánh giá chủ quan, tôi có thể giúp bạn hiểu:

**📖 Về mặt lý luận:**
- Định nghĩa chủ nghĩa xã hội theo 4 góc độ
- Đặc trưng bản chất của chủ nghĩa xã hội
- Quan điểm của Mác - Lênin về CNXH

**🏗️ Về mặt thực tiễn:**
- Thời kỳ quá độ lên chủ nghĩa xã hội
- Sự vận dụng của Đảng Cộng sản Việt Nam
- Mục tiêu và phương hướng xây dựng CNXH

### 💡 Câu hỏi học thuật phù hợp:
- "Chủ nghĩa xã hội là gì?"
- "Đặc trưng của chủ nghĩa xã hội?"
- "Thời kỳ quá độ có đặc điểm gì?"
- "Lênin nhấn mạnh điều gì?"

Hãy hỏi tôi về những khía cạnh học thuật này để có cái nhìn toàn diện! 📚"""
        else:
            response = f"""Xin lỗi, tôi là chatbot chuyên về **Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội**. 

Tôi không thể trả lời câu hỏi về chủ đề khác, nhưng tôi có thể giúp bạn tìm hiểu về:

### 📚 Các chủ đề tôi có thể hỗ trợ:
- **Định nghĩa chủ nghĩa xã hội** (4 góc độ tiếp cận)
- **Đặc trưng bản chất** của chủ nghĩa xã hội
- **Thời kỳ quá độ** lên chủ nghĩa xã hội
- **Quan điểm của Mác - Lênin** về chủ nghĩa xã hội
- **Sự vận dụng** của Đảng Cộng sản Việt Nam
- **Mục tiêu và phương hướng** xây dựng CNXH ở Việt Nam

### 💡 Gợi ý câu hỏi:
- "Chủ nghĩa xã hội là gì?"
- "Đặc trưng của chủ nghĩa xã hội?"
- "Thời kỳ quá độ có đặc điểm gì?"
- "Lênin nhấn mạnh điều gì?"

Hãy thử hỏi tôi về những chủ đề trên nhé! 😊"""
        
        return {
            "answer": response,
            "sources": ["Hướng dẫn sử dụng chatbot"],
            "confidence": 100
        }
    
    def get_full_chapter_content(self, chapter_name: str) -> str:
        """Đọc toàn bộ nội dung của một chương từ file .md"""
        book_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "book"))
        chapter_file = os.path.join(book_dir, f"{chapter_name}.md")
        
        try:
            if os.path.exists(chapter_file):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                print(f"File not found: {chapter_file}")
                return ""
        except Exception as e:
            print(f"Error reading file {chapter_file}: {e}")
            return ""

    def generate_response_with_sources(self, question: str):
        """Generate response với improved citations.
        - Nếu tìm thấy nội dung trong .md: chỉ được phép trả lời dựa trên các đoạn trích (không thêm kiến thức ngoài).
        - Nếu không tìm thấy: fallback sang Gemini trả lời chung (ghi rõ là không có trích dẫn .md).
        - Xử lý đặc biệt cho yêu cầu tóm tắt chương: đọc toàn bộ nội dung chương.
        """
        try:
            print(f"🎯 RAG SERVICE: Processing question: '{question}'")
            
            # Kiểm tra xem có phải yêu cầu tóm tắt chương không
            is_chapter_summary, chapter_name = self.detect_chapter_summary_request(question)
            
            if is_chapter_summary and chapter_name:
                print(f"📖 CHAPTER SUMMARY detected: {chapter_name}")
                # Xử lý đặc biệt cho tóm tắt chương
                return self._handle_chapter_summary(question, chapter_name)
            
            # Kiểm tra xem có phải yêu cầu tạo sơ đồ tư duy không
            if self.detect_mindmap_request(question):
                print(f"🧠 MINDMAP REQUEST detected!")
                return self._handle_mindmap_request(question)
            
            # Kiểm tra xem có phải câu hỏi không liên quan đến chủ nghĩa xã hội không
            if self.detect_off_topic_question(question):
                print(f"🚫 OFF-TOPIC QUESTION detected!")
                return self._handle_off_topic_question(question)
            
            # Tăng số lượng kết quả và ưu tiên đoạn chứa định nghĩa chuẩn
            search_results = self.vector_store.search(question, n_results=10)
            
            # Nếu hỏi về định nghĩa chủ nghĩa xã hội, tìm kiếm thêm đoạn định nghĩa 4 góc độ
            qn = self._normalize(question)
            if any(k in qn for k in ['chu nghia xa hoi la gi', 'chủ nghĩa xã hội là gì', 'định nghĩa chủ nghĩa xã hội']):
                print(f"🔍 Tìm kiếm thêm đoạn định nghĩa 4 góc độ...")
                def_search = self.vector_store.search('có thể được tiếp cận từ nhiều góc độ', n_results=3)
                if def_search['documents'][0]:
                    # Thêm đoạn định nghĩa vào đầu kết quả
                    search_results['documents'][0].insert(0, def_search['documents'][0][0])
                    search_results['metadatas'][0].insert(0, def_search['metadatas'][0][0])
                    search_results['scores'][0].insert(0, def_search['scores'][0][0])
                    print(f"Added 4-angle definition to results")

            # Tối ưu hóa: Giảm độ phức tạp của fallback logic
            min_score = float(os.getenv("MIN_RAG_SCORE", "0.05"))  # Giảm ngưỡng để ít fallback hơn
            scores = search_results.get('scores', [[]])[0] if isinstance(search_results.get('scores'), list) else []
            best_score = scores[0] if scores else 0.0
            
            # Lấy top 3 documents để đánh giá
            docs = search_results['documents'][0][:3] if search_results['documents'][0] else []
            
            # Debug logging (rút gọn)
            print(f"🔍 RAG DEBUG: score={best_score:.3f}, docs={len(docs)}")
            
            # Điều kiện fallback đơn giản - chỉ khi thực sự không có docs hoặc score quá thấp
            should_fallback = (not docs) or (best_score < min_score)
            print(f"   Final should fallback: {should_fallback}")
            
            if should_fallback:
                # Fallback: không có nội dung trong .md → trả lời trực tiếp bằng Gemini
                fallback_prompt = f"""TRẢ LỜI CÂU HỎI VỀ CHỦ NGHĨA XÃ HỘI VÀ THỜI KỲ QUÁ ĐỘ:

{question}

QUY TẮC NGHIÊM NGẶT:
- KHÔNG ĐƯỢC bắt đầu bằng "Với tư cách là...", "Tôi là...", "Chào bạn...", "là một chuyên gia..."
        - KHÔNG ĐƯỢC tự nhận là "chuyên gia về tư tưởng Hồ Chí Minh" hoặc bất kỳ chuyên gia nào khác
- KHÔNG ĐƯỢC giới thiệu bản thân
- BẮT ĐẦU NGAY bằng nội dung câu trả lời
- Tập trung vào nội dung Chương 03: Chủ nghĩa xã hội và thời kỳ quá độ
- Giọng điệu: Khách quan, học thuật

TRẢ LỜI NGAY:"""
                resp = self.model.generate_content(fallback_prompt)
                answer_text = resp.text or ""
                
                # Loại bỏ các cụm từ không mong muốn
                unwanted_phrases = [
                    "Với tư cách là một chuyên gia về tư tưởng Hồ Chí Minh",
                    "với tư cách là một chuyên gia về tư tưởng Hồ Chí Minh", 
                    "là một chuyên gia về tư tưởng Hồ Chí Minh",
                    "Chào bạn, là một chuyên gia về tư tưởng Hồ Chí Minh",
                    "chào bạn, là một chuyên gia về tư tưởng Hồ Chí Minh",
                    "Trong tư tưởng Hồ Chí Minh",
                    "trong tư tưởng Hồ Chí Minh",
                    "Theo tư tưởng Hồ Chí Minh",
                    "theo tư tưởng Hồ Chí Minh",
                    "Hồ Chí Minh cho rằng",
                    "hồ Chí Minh cho rằng",
                    "Với tư cách là",
                    "với tư cách là",
                    "Tôi là chuyên gia",
                    "tôi là chuyên gia"
                ]
                
                for phrase in unwanted_phrases:
                    if phrase in answer_text:
                        answer_text = answer_text.replace(phrase, "").strip()
                        # Loại bỏ dấu phẩy thừa ở đầu
                        if answer_text.startswith(","):
                            answer_text = answer_text[1:].strip()
                        if answer_text.startswith("tôi"):
                            answer_text = answer_text[3:].strip()
                        if answer_text.startswith("Tôi"):
                            answer_text = answer_text[3:].strip()
                
                # Làm sạch format (chỉ cơ bản)
                import re
                answer_text = re.sub(r'\n\s*\n+', '\n\n', answer_text)
                answer_text = answer_text.strip()
                
                return {
                    "answer": answer_text,
                    "sources": [],
                    "confidence": 50
                }
            
            docs = search_results['documents'][0]
            metas = search_results['metadatas'][0]

            # Re-rank theo mục đích câu hỏi
            qn = self._normalize(question)
            want_def = any(k in qn for k in ['khai niem', 'định nghĩa', 'dinh nghia', 'la gi', 'khai niệm'])
            # Ưu tiên phần II khi hỏi "đối tượng nghiên cứu"
            want_subject = ('doi tuong nghien cuu' in qn) or (('doi tuong' in qn) and ('nghien cuu' in qn))
            def contains_def(txt: str) -> bool:
                tn = self._normalize(txt)
                return ('tu tuong ho chi minh la' in tn) or ('nêu khái niệm' in txt.lower()) or ('co the duoc tiep can tu nhieu goc do' in tn) or ('phong trao thuc tien' in tn and 'trao luu tu tuong' in tn)
            def contains_subject(txt: str) -> bool:
                tn = self._normalize(txt)
                return ('doi tuong nghien cuu' in tn)

            pairs = list(zip(docs, metas))
            if want_def:
                pairs.sort(key=lambda p: 0 if contains_def(p[0]) else 1)
            elif want_subject:
                pairs.sort(key=lambda p: 0 if contains_subject(p[0]) else 1)

            # Lấy tối đa 4 đoạn để có đủ ngữ cảnh
            top_pairs = pairs[:4]
            context_docs = [p[0] for p in top_pairs]
            source_metadatas = [p[1] for p in top_pairs]
            
            context = ""
            sources_used = []
            
            for i, (doc, metadata) in enumerate(zip(context_docs[:3], source_metadatas[:3])):
                source_detail = metadata.get('source', 'Unknown')
                document_title = metadata.get('document', '')
                page_info = metadata.get('page', '')

                # Nhãn ngắn gọn chỉ ghi chương
                short_label = self._slug_to_title(page_info) if page_info else (document_title or 'Nguồn')

                # Context không hiển thị citation
                context += f"{doc}\n"

                # Link mở trang book và highlight đúng trích đoạn (giữ href đầy đủ)
                snippet = (doc or '').strip().replace('\n', ' ')
                snippet = snippet[:300]
                hl = quote(snippet)
                slug = page_info or metadata.get('page', '')
                href = f"book/chuong3.html#{slug}?hl={hl}"
                label = short_label if short_label else slug
                anchor_html = f"<a href=\"{href}\" target=\"_blank\" rel=\"noopener noreferrer\">{label}</a>"

                sources_used.append({
                    "source": anchor_html,
                    "credibility": metadata.get('credibility_score', 100),
                    "type": metadata.get('source_type', 'official'),
                    "url": href,
                    "document": document_title
                })
            
            prompt = f"""TRẢ LỜI CÂU HỎI VỀ CHỦ NGHĨA XÃ HỘI VÀ THỜI KỲ QUÁ ĐỘ:

TÀI LIỆU THAM KHẢO:
{context}

CÂU HỎI: {question}

QUY TẮC NGHIÊM NGẶT:
- KHÔNG ĐƯỢC bắt đầu bằng "Với tư cách là...", "Tôi là...", "Chào bạn...", "là một chuyên gia..."
        - KHÔNG ĐƯỢC tự nhận là "chuyên gia về tư tưởng Hồ Chí Minh" hoặc bất kỳ chuyên gia nào khác
- KHÔNG ĐƯỢC giới thiệu bản thân
        - KHÔNG ĐƯỢC bắt đầu bằng "Trong tư tưởng Hồ Chí Minh..." hoặc bất kỳ tư tưởng nào khác
        - KHÔNG ĐƯỢC bắt đầu bằng "Theo tư tưởng Hồ Chí Minh..." hoặc bất kỳ tư tưởng nào khác
- KHÔNG ĐƯỢC bắt đầu bằng "Hồ Chí Minh cho rằng..."
- BẮT ĐẦU NGAY bằng nội dung câu trả lời về chủ nghĩa xã hội
- CHỈ sử dụng thông tin từ tài liệu được cung cấp
- Dùng tiêu đề markdown (##, ###) và bullet points
- Giọng điệu: Khách quan, học thuật, dựa trên tài liệu
- Tập trung vào nội dung chủ nghĩa xã hội và thời kỳ quá độ

HƯỚNG DẪN TRẢ LỜI CỤ THỂ:
- Nếu câu hỏi về "Chủ nghĩa xã hội là gì?", BẮT BUỘC trả lời theo đúng 4 góc độ trong tài liệu:
  1. Là phong trào thực tiễn – phong trào đấu tranh của nhân dân lao động chống lại áp bức, bất công, chống lại giai cấp thống trị
  2. Là trào lưu tư tưởng – lý luận phản ánh lý tưởng giải phóng nhân dân lao động khỏi áp bức, bóc lột
  3. Là một khoa học – chủ nghĩa xã hội khoa học là khoa học về sứ mệnh lịch sử của giai cấp công nhân
  4. Là một chế độ xã hội tốt đẹp, là giai đoạn đầu của hình thái kinh tế – xã hội cộng sản chủ nghĩa
- Nếu câu hỏi về đặc trưng, trả lời theo 6 đặc trưng: giải phóng con người, nền kinh tế phát triển cao, nhân dân làm chủ, văn hóa mới, công bằng bình đẳng, quá trình phát triển lâu dài
- Nếu câu hỏi về thời kỳ quá độ, trả lời theo khái niệm, tính tất yếu, đặc điểm
- Luôn trích dẫn chính xác từ tài liệu, không tự suy diễn

QUAN TRỌNG: Nếu tài liệu có đoạn "Chủ nghĩa xã hội có thể được tiếp cận từ nhiều góc độ khác nhau", BẮT BUỘC sử dụng đoạn đó làm câu trả lời chính và trích dẫn đầy đủ 4 góc độ.

CẤU TRÚC TRẢ LỜI BẮT BUỘC:
- Bắt đầu bằng: "Chủ nghĩa xã hội có thể được tiếp cận từ 4 góc độ khác nhau:"
- Liệt kê đầy đủ 4 góc độ theo đúng thứ tự trong tài liệu:
  1. Là phong trào thực tiễn – phong trào đấu tranh của nhân dân lao động chống lại áp bức, bất công, chống lại giai cấp thống trị
  2. Là trào lưu tư tưởng – lý luận phản ánh lý tưởng giải phóng nhân dân lao động khỏi áp bức, bóc lột
  3. Là một khoa học – chủ nghĩa xã hội khoa học là khoa học về sứ mệnh lịch sử của giai cấp công nhân
  4. Là một chế độ xã hội tốt đẹp, là giai đoạn đầu của hình thái kinh tế – xã hội cộng sản chủ nghĩa
- Không được thêm nội dung khác vào phần định nghĩa cơ bản

TRẢ LỜI NGAY:
"""

            # Ưu tiên trích nguyên văn nếu tìm thấy định nghĩa chính xác
            # (được hướng dẫn ngay trong prompt)
            response = self.model.generate_content(prompt)
            answer_text = response.text or ""
            
            # Xử lý đặc biệt cho câu hỏi về định nghĩa chủ nghĩa xã hội
            if any(k in qn for k in ['chu nghia xa hoi la gi', 'chủ nghĩa xã hội là gì', 'định nghĩa chủ nghĩa xã hội']):
                # Kiểm tra xem có đoạn định nghĩa 4 góc độ trong context không
                if any('có thể được tiếp cận từ nhiều góc độ' in doc for doc in context_docs):
                    print(f"Detected 4-angle definition, creating standard answer...")
                    answer_text = """Chủ nghĩa xã hội có thể được tiếp cận từ 4 góc độ khác nhau:

1. **Là phong trào thực tiễn** – phong trào đấu tranh của nhân dân lao động chống lại áp bức, bất công, chống lại giai cấp thống trị.

2. **Là trào lưu tư tưởng** – lý luận phản ánh lý tưởng giải phóng nhân dân lao động khỏi áp bức, bóc lột.

3. **Là một khoa học** – chủ nghĩa xã hội khoa học là khoa học về sứ mệnh lịch sử của giai cấp công nhân.

4. **Là một chế độ xã hội tốt đẹp**, là giai đoạn đầu của hình thái kinh tế – xã hội cộng sản chủ nghĩa."""
                    print(f"Created standard 4-angle answer")
                    # Bỏ qua xử lý post-processing cho câu trả lời đặc biệt này
                    return {
                        "answer": answer_text,
                        "sources": sources_used,
                        "confidence": 95
                    }
            
            # Loại bỏ các cụm từ không mong muốn
            unwanted_phrases = [
                "Với tư cách là một chuyên gia về tư tưởng Hồ Chí Minh",
                "với tư cách là một chuyên gia về tư tưởng Hồ Chí Minh", 
                "là một chuyên gia về tư tưởng Hồ Chí Minh",
                "Chào bạn, là một chuyên gia về tư tưởng Hồ Chí Minh",
                "chào bạn, là một chuyên gia về tư tưởng Hồ Chí Minh",
                "Trong tư tưởng Hồ Chí Minh",
                "trong tư tưởng Hồ Chí Minh",
                "Theo tư tưởng Hồ Chí Minh",
                "theo tư tưởng Hồ Chí Minh",
                "Hồ Chí Minh cho rằng",
                "hồ Chí Minh cho rằng",
                "Với tư cách là",
                "với tư cách là",
                "Tôi là chuyên gia",
                "tôi là chuyên gia"
            ]
            
            for phrase in unwanted_phrases:
                if phrase in answer_text:
                    answer_text = answer_text.replace(phrase, "").strip()
                    # Loại bỏ dấu phẩy thừa ở đầu
                    if answer_text.startswith(","):
                        answer_text = answer_text[1:].strip()
                    if answer_text.startswith("tôi"):
                        answer_text = answer_text[3:].strip()
                    if answer_text.startswith("Tôi"):
                        answer_text = answer_text[3:].strip()
            
            # Làm sạch format text (chỉ giữ lại basic cleaning)
            import re
            # Xóa dòng trống thừa và chuẩn hóa khoảng trắng
            answer_text = re.sub(r'\n\s*\n+', '\n\n', answer_text)
            answer_text = re.sub(r'^\s*\n', '', answer_text)
            answer_text = answer_text.strip()

            # GIỮ NGUYÊN citations với text đầy đủ để có thể highlight
            # Không rút gọn nữa vì cần text để highlight trên book page
            # for j, md in enumerate(source_metadatas[:3], start=1):
            #     slug = (md.get('page', '') or '').strip()
            #     short = self._slug_to_title(slug) if slug else ''
            #     if short:
            #         pattern = rf"\[Nguồn\s*{j}\s*-[^\]]*\]"
            #         replacement = f"[Nguồn {j} - {short}]"
            #         answer_text = re.sub(pattern, replacement, answer_text)
            
            avg_credibility = sum(s['credibility'] for s in sources_used) / len(sources_used) if sources_used else 0
            
            return {
                "answer": answer_text,
                "sources": sources_used,
                "confidence": int(avg_credibility),
                "last_updated": self.last_update.isoformat() if self.last_update else datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return {
                "answer": "Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi. Vui lòng thử lại sau.",
                "sources": [],
                "confidence": 0
            }
    
    def _handle_chapter_summary(self, question: str, chapter_name: str):
        """Xử lý đặc biệt cho yêu cầu tóm tắt chương"""
        try:
            # Đọc toàn bộ nội dung chương
            full_content = self.get_full_chapter_content(chapter_name)
            
            if not full_content:
                return {
                    "answer": f"Không tìm thấy nội dung của {self._slug_to_title(chapter_name)}.",
                    "sources": [],
                    "confidence": 0
                }
            
            # Chia nhỏ nội dung thành các phần để AI có thể xử lý
            # Giới hạn độ dài để tránh vượt quá context window
            max_content_length = 15000  # Giữ lại đủ space cho prompt và response
            if len(full_content) > max_content_length:
                # Chia thành các phần nhỏ hơn
                content_parts = self.split_text(full_content, max_length=max_content_length//3)
                # Lấy 3 phần đầu tiên để đảm bảo có overview tốt  
                summary_content = "\n\n".join(content_parts[:3])
            else:
                summary_content = full_content
            
            chapter_title = self._slug_to_title(chapter_name)
            
            # Tạo prompt đặc biệt cho tóm tắt chương
            prompt = f"""Hãy tóm tắt {chapter_title} về Chủ nghĩa xã hội và thời kỳ quá độ lên chủ nghĩa xã hội dựa trên nội dung sau:

{summary_content}

YÊU CẦU TÓM TẮT:
- Tạo một bản tóm tắt toàn diện và có cấu trúc cho {chapter_title}
- Sử dụng tiêu đề markdown (##, ###) để chia các mục chính
- Trình bày các ý chính bằng danh sách bullet points
- Nêu rõ các khái niệm và định nghĩa quan trọng
- Làm nổi bật những khái niệm và lý luận cốt lõi trong chương này
- Trả lời bằng tiếng Việt, văn phong học thuật nhưng dễ hiểu
- Độ dài: 800-1200 từ

Bắt đầu tóm tắt:"""
            
            response = self.model.generate_content(prompt)
            answer_text = response.text or ""
            
            # Tạo source thông tin cho chương
            source_info = {
                "source": f"<a href=\"book/tu-tuong-ho-chi-minh.html#{chapter_name}\" target=\"_blank\" rel=\"noopener noreferrer\">{chapter_title}</a>",
                "credibility": 100,
                "type": "document",
                "url": f"book/tu-tuong-ho-chi-minh.html#{chapter_name}",
                "document": chapter_title
            }
            
            return {
                "answer": answer_text,
                "sources": [source_info],
                "confidence": 95,
                "last_updated": self.last_update.isoformat() if self.last_update else datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in chapter summary: {e}")
            return {
                "answer": f"Xin lỗi, có lỗi xảy ra khi tóm tắt {self._slug_to_title(chapter_name)}. Vui lòng thử lại sau.",
                "sources": [],
                "confidence": 0
            }
    
    def _handle_mindmap_request(self, question: str):
        """Xử lý yêu cầu tạo sơ đồ tư duy"""
        try:
            # Trích xuất chủ đề từ câu hỏi
            topic = self._extract_mindmap_topic(question)
            
            # Kiểm tra nếu là request về chương cụ thể
            import re
            chapter_match = re.search(r'chương\s*(\d+)', topic.lower())
            if chapter_match:
                chapter_num = chapter_match.group(1)
                chapter_name = f"chuong{chapter_num}"
                
                # Đọc toàn bộ nội dung chương
                chapter_content = self.get_full_chapter_content(chapter_name)
                
                if chapter_content:
                    # Cắt ngắn nội dung để tránh vượt quá context limit và timeout
                    max_content = 8000  # Giảm từ 12000 xuống 8000
                    if len(chapter_content) > max_content:
                        # Lấy phần đầu và tóm tắt
                        chapter_content = chapter_content[:max_content] + "\n\n[Nội dung đã được rút gọn để tối ưu hóa...]"
                    
                    relevant_content = chapter_content
                    chapter_title = self._slug_to_title(chapter_name)
                    
                    source_info = {
                        "source": f"<a href=\"book/tu-tuong-ho-chi-minh.html#{chapter_name}\" target=\"_blank\" rel=\"noopener noreferrer\">{chapter_title}</a>",
                        "credibility": 100,
                        "type": "mindmap",
                        "url": f"book/tu-tuong-ho-chi-minh.html#{chapter_name}",
                        "document": f"Sơ đồ tư duy {chapter_title}"
                    }
                else:
                    # Fallback nếu không tìm thấy file chương
                    search_results = self.vector_store.search(topic, n_results=8)
                    relevant_content = "\n\n".join(search_results['documents'][0][:6]) if search_results['documents'][0] else ""
                    source_info = {
                        "source": "Giáo trình Chủ nghĩa xã hội khoa học (K-2021)",
                        "credibility": 85,
                        "type": "mindmap",
                        "url": "",
                        "document": "Sơ đồ tư duy"
                    }
            else:
                # Tìm kiếm thông tin liên quan đến chủ đề thông thường
                search_results = self.vector_store.search(topic, n_results=8)
                
                if not search_results['documents'][0]:
                    # Không có thông tin liên quan, tạo mindmap tổng quát
                    return self._create_general_mindmap(topic)
                
                # Lấy nội dung liên quan
                relevant_content = "\n\n".join(search_results['documents'][0][:6])
                source_info = {
                    "source": "Giáo trình Chủ nghĩa xã hội khoa học (K-2021)",
                    "credibility": 95,
                    "type": "mindmap",
                    "url": "",
                    "document": "Sơ đồ tư duy"
                }
            
            if relevant_content:
                
                # Tạo prompt với syntax đúng cho Mermaid mindmap
                prompt = f"""Tạo Mermaid mindmap cho: "{topic}"

Nội dung: {relevant_content[:3000]}...

QUAN TRỌNG - Format CHÍNH XÁC (cần đúng indentation):

```mermaid
mindmap
  root(({topic}))
    Nhánh chính 1
      Ý con 1
      Ý con 2
    Nhánh chính 2
      Ý con 1
      Ý con 2
```

QUY TẮC:
- root() có 2 spaces
- Nhánh chính có 4 spaces  
- Ý con có 6 spaces
- Tối đa 4 nhánh chính, mỗi nhánh 3-4 ý con
- Text ngắn gọn (<15 từ mỗi node)

Chỉ trả về mermaid code:"""
                
                # Tối ưu hóa generation config
                import google.generativeai as genai
                generation_config = genai.types.GenerationConfig(
                    temperature=0.3,  # Giảm temperature để tăng tốc
                    max_output_tokens=2048,  # Giảm output tokens để tăng tốc
                    top_p=0.8,
                    top_k=10
                )
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                # Debug Gemini response chi tiết 
                print(f"🤖 Gemini response type: {type(response)}")
                
                # Check safety filters và finish reason
                if hasattr(response, 'prompt_feedback'):
                    print(f"🛡️ prompt_feedback: {response.prompt_feedback}")
                
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    print(f"🏁 finish_reason: {getattr(candidate, 'finish_reason', 'Unknown')}")
                    print(f"🛡️ safety_ratings: {getattr(candidate, 'safety_ratings', [])}")
                    print(f"🔍 candidate.content.parts: {len(candidate.content.parts)} parts")
                
                # Nếu không có parts, có thể bị block - thử prompt đơn giản hơn
                if hasattr(response, 'candidates') and response.candidates and len(response.candidates[0].content.parts) == 0:
                    print("⚠️ No content parts found - possible content blocked. Trying simple fallback...")
                    
                    # Fallback với prompt siêu đơn giản
                    simple_prompt = f"""Create a simple mindmap about: {topic}

Format:
```mermaid
mindmap
  root((Topic))
    Branch 1
      Item A  
      Item B
    Branch 2
      Item C
      Item D
```"""
                    
                    print(f"🔄 Trying simplified prompt...")
                    fallback_response = self.model.generate_content(simple_prompt)
                    
                    try:
                        mermaid_code = fallback_response.text or ""
                        print(f"✅ Fallback successful: {len(mermaid_code)} chars")
                    except:
                        mermaid_code = f"""```mermaid
mindmap
  root(({topic}))
    Nội dung chính
      Khái niệm cơ bản
      Ý nghĩa quan trọng
    Ứng dụng thực tế
      Trong học tập
      Trong cuộc sống
```"""
                        print(f"🔧 Using hardcoded fallback mindmap")
                else:
                    # Normal extraction
                    try:
                        mermaid_code = response.text or ""
                        print(f"✅ Successfully got response.text: {len(mermaid_code)} chars")
                    except Exception as e:
                        print(f"⚠️ response.text failed: {e}")
                        # Extract từ parts như trước
                        if hasattr(response, 'candidates') and response.candidates:
                            parts = response.candidates[0].content.parts
                            if parts:
                                all_text = ""
                                for part in parts:
                                    all_text += getattr(part, 'text', '') or ''
                                mermaid_code = all_text
                            else:
                                mermaid_code = ""
                        else:
                            mermaid_code = ""
                
                print(f"📄 Final mermaid_code preview: {mermaid_code[:100]}...")
                
                # Kiểm tra và làm sạch mermaid code
                mermaid_code = self._clean_mermaid_code(mermaid_code)
                
                return {
                    "answer": f"## Sơ đồ tư duy: {topic}\n\n{mermaid_code}",
                    "sources": [source_info],
                    "confidence": 90,
                    "last_updated": datetime.now().isoformat()
                }
            else:
                # Không có thông tin liên quan, tạo mindmap tổng quát
                return self._create_general_mindmap(topic)
                
        except Exception as e:
            print(f"Error in mindmap generation: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể tạo sơ đồ tư duy lúc này. Vui lòng thử lại sau.",
                "sources": [],
                "confidence": 0
            }
    
    def _extract_mindmap_topic(self, question: str) -> str:
        """Trích xuất chủ đề chính từ yêu cầu mindmap"""
        import re
        q_lower = question.lower()
        
        # Tìm pattern với nhiều dạng khác nhau
        patterns = [
            # Sơ đồ tư duy patterns
            r'tạo.*?sơ đồ tư duy.*?cho\s*(.+)',
            r'tạo.*?sơ đồ tư duy.*?về\s*(.+)',
            r'tạo.*?sơ đồ tư duy.*?:\s*(.+)',
            # Vẽ sơ đồ patterns
            r'vẽ.*?sơ đồ.*?về\s*(.+)',
            r'vẽ.*?sơ đồ.*?cho\s*(.+)',
            r'vẽ.*?sơ đồ.*?:\s*(.+)',
            # Sơ đồ về patterns
            r'sơ đồ.*?về\s*(.+)',
            r'sơ đồ.*?cho\s*(.+)',
            r'sơ đồ.*?:\s*(.+)',
            # Mindmap patterns
            r'mindmap.*?cho\s*(.+)',
            r'mindmap.*?về\s*(.+)',
            r'mindmap.*?:\s*(.+)',
            # Tạo sơ đồ patterns
            r'tạo.*?sơ đồ.*?về\s*(.+)',
            r'tạo.*?sơ đồ.*?cho\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, q_lower)
            if match:
                topic = match.group(1).strip()
                
                # Xử lý đặc biệt cho "nội dung chương X"
                chapter_match = re.search(r'nội dung\s*(chương|chưong)\s*(\d+|[ivxlc]+)', topic)
                if chapter_match:
                    chapter_num = chapter_match.group(2)
                    # Chuyển đổi số La Mã nếu cần
                    roman_to_num = {'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5', 'vi': '6'}
                    if chapter_num.lower() in roman_to_num:
                        chapter_num = roman_to_num[chapter_num.lower()]
                    return f"Nội dung Chương {chapter_num}"
                
                # Xử lý trực tiếp "chương X"
                chapter_direct = re.search(r'(chương|chưong)\s*(\d+|[ivxlc]+)', topic)
                if chapter_direct:
                    chapter_num = chapter_direct.group(2)
                    roman_to_num = {'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5', 'vi': '6'}
                    if chapter_num.lower() in roman_to_num:
                        chapter_num = roman_to_num[chapter_num.lower()]
                    return f"Chương {chapter_num}"
                
                # Loại bỏ các từ không cần thiết
                topic = re.sub(r'(hồ chí minh|hcm)', '', topic).strip()
                return topic.title() if topic else "Chủ nghĩa xã hội và thời kỳ quá độ"
        
        # Nếu không tìm thấy, trả về chủ đề mặc định
        return "Chủ nghĩa xã hội và thời kỳ quá độ"
    
    def _clean_mermaid_code(self, code: str) -> str:
        """Làm sạch và chuẩn hóa Mermaid code"""
        if not code:
            return ""
        
        # Loại bỏ các dòng giải thích
        lines = code.split('\n')
        mermaid_lines = []
        in_mermaid = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('```mermaid'):
                in_mermaid = True
                mermaid_lines.append(line)
            elif line.startswith('```') and in_mermaid:
                mermaid_lines.append(line)
                break
            elif in_mermaid:
                mermaid_lines.append(line)
        
        if not mermaid_lines:
            # Nếu không có mermaid block, thêm vào
            return f"```mermaid\n{code}\n```"
        
        return '\n'.join(mermaid_lines)
    
    def _create_general_mindmap(self, topic: str):
        """Tạo mindmap tổng quát khi không có thông tin cụ thể"""
        general_mindmap = f"""```mermaid
mindmap
  root(({topic}))
    Tư tưởng chính trị
        Độc lập dân tộc
        Dân chủ nhân dân
        Chủ nghĩa xã hội
    Tư tưởng đạo đức
        Cần kiệm liêm chính
        Sống và làm việc có kế hoạch
        Đoàn kết yêu thương
    Tư tưởng giáo dục
        Học để làm người
        Kết hợp lý thuyết và thực tiễn
        Giáo dục toàn diện
    Tư tưởng văn hóa
        Dân tộc - Khoa học - Đại chúng
        Kế thừa và phát triển
        Giữ gìn bản sắc dân tộc
```"""
        
        return {
            "answer": f"## Sơ đồ tư duy: {topic}\n\n{general_mindmap}",
            "sources": [{
                "source": "Giáo trình Chủ nghĩa xã hội khoa học (K-2021)",
                "credibility": 85,
                "type": "mindmap",
                "url": "",
                "document": "Sơ đồ tư duy tổng quát"
            }],
            "confidence": 80,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_stats(self):
        return {
            "total_documents": self.vector_store.get_collection_count(),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "trusted_sources_count": 0,  # Disabled external data collection
            "status": "ready",
            "features": ["chapter_summary", "mindmap_generation", "rag_search"]
        }
