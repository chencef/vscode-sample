import streamlit as st
from openocr import OpenOCR
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 初始化 OCR 引擎
engine = OpenOCR()

# Streamlit 標題
st.title("OCR 辨識工具")

# 上傳圖片
uploaded_file = st.file_uploader("請選擇一個圖片檔案", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 讀取上傳的圖片
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        st.error("無法讀取圖片，請檢查檔案格式")
    else:
        # 將 OpenCV 圖片轉換為 PIL 圖片
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)

        # 加載中文字型
        font_path = "c:/Users/111/vscode-ai/1/SimHei.ttf"  # 請替換為實際的中文字型路徑
        try:
            font = ImageFont.truetype(font_path, 20)
        except IOError:
            st.error("無法打開字型檔案，請檢查字型檔案路徑")
            st.stop()

        # 使用 OCR 辨識文字
        result = engine(uploaded_file.name)
        if len(result) > 0 and isinstance(result[0], list):
            json_string = result[0][0]  # 取出第一部分的字串
            try:
                # 提取 JSON 部分並解析
                parsed_data = json.loads(json_string.split("\t")[1])
                for item in parsed_data:
                    transcription = item.get("transcription", "無法取得 transcription")
                    points = item.get("points", [])

                    # 確保有四個點
                    if len(points) == 4:
                        # 使用紅色線條連接四個點
                        draw.line([tuple(points[0]), tuple(points[1]), tuple(points[2]), tuple(points[3]), tuple(points[0])],
                                  fill=(255, 0, 0), width=2)

                        # 計算文字框的高度和寬度
                        height = abs(points[0][1] - points[2][1])
                        width = abs(points[0][0] - points[1][0])

                        # 動態調整文字大小
                        font_size = max(10, min(height, width) // 2)
                        font = ImageFont.truetype(font_path, font_size)

                        # 計算文字位置（框的中間）
                        bbox = font.getbbox(transcription)
                        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                        text_x = points[0][0] + (width - text_width) // 2
                        text_y = points[0][1] + (height - text_height) // 2

                        # 在框內添加文字（藍色）
                        draw.text((text_x, text_y), transcription, font=font, fill=(0, 0, 255, 255))

                # 顯示結果圖片
                st.image(image_pil, caption="辨識結果", use_column_width=True)

            except json.JSONDecodeError as e:
                st.error(f"JSON 解析失敗: {e}")
        else:
            st.warning("未能辨識出任何文字")