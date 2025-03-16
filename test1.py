# 產生一個 Streamlit 範例程式    test

from openocr import OpenOCR
import json  # 用於解析 JSON 格式的資料
import cv2  # 用於圖像處理
import numpy as np  # 用於處理座標點
from PIL import ImageFont, ImageDraw, Image  # 用於處理中文字型

engine = OpenOCR()
img_path = 'oo1.jpg'
result = engine(img_path)

# 打印 result 的結構
print("Result 的類型:", type(result))
print("Result 的內容:", result)

# 讀取圖片
image = cv2.imread(img_path)
if image is None:
    print("無法讀取圖片，請檢查圖片路徑")
    exit()

# 將 OpenCV 圖片轉換為 PIL 圖片
image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(image_pil)

# 加載中文字型
font_path = "c:/Users/111/vscode-ai/1/SimHei.ttf"  # 請替換為實際的中文字型路徑
try:
    font = ImageFont.truetype(font_path, 20)
except IOError:
    print("無法打開字型檔案，請檢查字型檔案路徑")
    exit()

# 處理第一部分：解析 JSON 格式的字串
if len(result) > 0 and isinstance(result[0], list):
    json_string = result[0][0]  # 取出第一部分的字串
    try:
        # 提取 JSON 部分並解析
        parsed_data = json.loads(json_string.split("\t")[1])
        for item in parsed_data:
            transcription = item.get("transcription", "無法取得 transcription")
            points = item.get("points", [])
            if len(points) == 4:
                # 繪製多邊形框
                points_array = np.array(points, dtype=np.int32)
                cv2.polylines(image, [points_array], isClosed=True, color=(0, 255, 0), thickness=2)
                
                # 計算文字框的高度和寬度
                height = abs(points[0][1] - points[2][1])
                width = abs(points[0][0] - points[1][0])
                
                # 動態調整文字大小
                font_size = max(10, min(height, width) // 2)
                font = ImageFont.truetype(font_path, font_size)
                
                # 在框內添加文字
                x, y = points[0]  # 使用第一個點作為文字的起始位置
                draw.text((x, y), transcription, font=font, fill=(0, 255, 0, 255))
    except json.JSONDecodeError as e:
        print("JSON 解析失敗:", e)

# 將 PIL 圖片轉換回 OpenCV 圖片
image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

# 處理第二部分：時間相關的字典
if len(result) > 1 and isinstance(result[1], list):
    time_data = result[1][0]  # 取出時間相關的字典
    if isinstance(time_data, dict):
        print("第二部分的內容:")
        for key, value in time_data.items():
            print(f"{key}: {value}")

# 儲存結果圖片
output_path = 'output.jpg'
cv2.imwrite(output_path, image)
print(f"結果已儲存為 {output_path}")