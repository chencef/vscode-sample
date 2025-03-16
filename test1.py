# 產生一個 Streamlit 範例程式    test

from openocr import OpenOCR
import json  # 用於解析 JSON 格式的資料
import cv2  # 用於圖像處理
import numpy as np  # 用於處理座標點
from PIL import ImageFont, ImageDraw, Image  # 用於處理中文字型
import logging  # 用於調整日誌級別
import warnings  # 用於忽略警告訊息

# 設置 openocr 和 openrec 的日誌級別為 CRITICAL
logging.getLogger('openocr').setLevel(logging.CRITICAL)
logging.getLogger('openrec').setLevel(logging.CRITICAL)

# 忽略所有警告訊息
warnings.filterwarnings("ignore")

engine = OpenOCR()
img_path = 'oo2.jpg'
result = engine(img_path)

# 打印 result 的結構
# print("Result 的類型:", type(result))
# print("Result 的內容:", result)

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
            
            # 調試輸出 points
            print(f"辨識出的點位: {points}")
            
            if len(points) == 4:
                # 檢查 points 是否在圖片範圍內
                valid_points = True
                for point in points:
                    if point[0] < 0 or point[1] < 0 or point[0] >= image_pil.width or point[1] >= image_pil.height:
                        print(f"點位 {point} 超出圖片範圍")
                        valid_points = False
                        break

                if not valid_points:
                    print("點位超出範圍，跳過該項目")
                    continue

                # 使用紅色線條連接四個點
                print(f"正在繪製線條，點位: {points}")
                draw.line([tuple(points[0]), tuple(points[1]), tuple(points[2]), tuple(points[3]), tuple(points[0])],
                          fill=(255, 0, 0), width=2)

                # 計算文字框的高度和寬度
                height = abs(points[0][1] - points[2][1])
                width = abs(points[0][0] - points[1][0])

                # 動態調整文字大小
                font_size = max(10, min(height, width) // 2)
                font = ImageFont.truetype(font_path, font_size)

                # 計算文字位置（框的中間）
                bbox = font.getbbox(transcription)  # 使用 font.getbbox 替代 getsize
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                text_x = points[0][0] + (width - text_width) // 2
                text_y = points[0][1] + (height - text_height) // 2

                # 在框內添加文字（藍色）
                draw.text((text_x, text_y), transcription, font=font, fill=(0, 0, 255, 255))  # 在框內中間顯示文字

    except json.JSONDecodeError as e:
        print("JSON 解析失敗:", e)

# 將 PIL 圖片轉換回 OpenCV 圖片
image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

# 儲存結果圖片
output_path = 'output.jpg'
cv2.imwrite(output_path, image)
print(f"結果已儲存為 {output_path}")