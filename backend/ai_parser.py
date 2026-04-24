import json
import os
import time

import pandas as pd
import pdfplumber
from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_api_key():
    load_dotenv(override=True)
    return os.getenv("GEMINI_API_KEY")


async def parse_file(file_path: str, filename: str) -> list:
    ext = os.path.splitext(filename)[1].lower()
    raw_text = ""

    if ext in [".xlsx", ".xls", ".csv"]:
        try:
            if ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            raw_text = df.to_string(index=False)[:35000]
        except Exception as e:
            raise Exception(f"Lỗi đọc file Excel: {e}")

    elif ext == ".pdf":
        try:
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        raw_text += text + "\n"
                    if idx > 10:
                        break
        except Exception as e:
            raise Exception(f"Lỗi đọc file PDF: {e}")
    else:
        raise Exception("Định dạng file hỗ trợ là PDF, XLSX hoặc CSV.")

    if len(raw_text.strip()) < 10:
        raise Exception(
            "Không thể trích xuất văn bản từ file "
            "(file rỗng hoặc nội dung là hình ảnh không nhận diện được)."
        )

    return extract_with_gemini(raw_text)


def extract_with_gemini(text: str) -> list:
    api_key = get_api_key()
    if not api_key:
        raise Exception("Không tìm thấy GEMINI_API_KEY trong cấu hình hệ thống (.env).")

    prompt = (
        "Bạn là một chuyên gia phân tích báo giá thiết bị Smarthome/Điện.\n"
        "Nhiệm vụ của bạn là nhận diện và trích xuất danh sách tất cả các "
        "sản phẩm/vật tư từ đoạn văn bản thô (được chuyển từ PDF/Excel) dưới đây.\n\n"
        "YÊU CẦU ĐẦU RA:\n"
        "Trả về DUY NHẤT một mảng JSON. Mỗi object chỉ chứa các key sau:\n"
        "[\n"
        "  {\n"
        '    "sku": "Mã sản phẩm",\n'
        '    "description": "Mô tả / Tên sản phẩm",\n'
        '    "category": "Danh mục sản phẩm",\n'
        '    "brand": "Thương hiệu / Nhà sản xuất",\n'
        '    "image_url": "URL hình ảnh sản phẩm",\n'
        '    "details": "Thông số kỹ thuật / ghi chú",\n'
        '    "list_price": 0,\n'
        '    "input_price": 0,\n'
        '    "sell_price": 0\n'
        "  }\n"
        "]\n"
        "Nếu không có mã sản phẩm rõ ràng, hãy tự đặt một mã ngắn phù hợp.\n"
        "Không trả lời thêm bằng văn bản ngoài JSON.\n\n"
        "Dữ liệu nguồn:\n"
        + text[:35000]
    )

    try:
        response = None
        for attempt in range(5):
            try:
                with genai.Client(api_key=api_key) as client:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config={"response_mime_type": "application/json"},
                    )
                break
            except Exception as e:
                err_str = str(e)
                is_retryable = (
                    "429" in err_str
                    or "quota" in err_str.lower()
                    or "503" in err_str
                    or "unavailable" in err_str.lower()
                    or "high demand" in err_str.lower()
                )
                if is_retryable and attempt < 4:
                    wait_seconds = min(20 * (attempt + 1), 90)
                    print(
                        "Gemini temporarily unavailable. "
                        f"Waiting {wait_seconds} seconds before retry {attempt + 1}..."
                    )
                    time.sleep(wait_seconds)
                    continue
                raise

        res_text = (response.text or "").strip()
        if res_text.startswith("```json"):
            res_text = res_text[7:]
        elif res_text.startswith("```"):
            res_text = res_text[3:]
        if res_text.endswith("```"):
            res_text = res_text[:-3]

        data = json.loads(res_text.strip())
        if isinstance(data, list):
            return data
        raise Exception("Kết quả định dạng AI không phải là danh sách hợp lệ.")
    except Exception as e:
        raise Exception(f"Lỗi AI trích xuất (Gemini API): {e}")
