import cv2
import numpy as np
from openocr import OpenOCR
from PIL import Image, ImageDraw, ImageFont
import json  # 修復：匯入 json 模組

# 初始化 OCR 引擎
engine = OpenOCR()

# 讀取圖片
img_path = 'ooo3.jpg'
image = cv2.imread(img_path)
if image is None:
    print("無法讀取圖片，請檢查圖片路徑")
    exit()

# 將圖片轉換為 HSV 顏色空間
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定義紅色的 HSV 範圍
lower_red1 = np.array([0, 120, 70])  # 紅色範圍1
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])  # 紅色範圍2
upper_red2 = np.array([180, 255, 255])

# 創建紅色遮罩
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
red_mask = cv2.bitwise_or(mask1, mask2)

# 找到紅色框的輪廓
contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

# 使用 OCR 辨識文字
result = engine(img_path)
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
                # 計算文字框的右邊界
                text_right = max(p[0] for p in points)

                # 遍歷紅色框的輪廓，檢查是否在文字右方
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if x > text_right:  # 紅色框在文字右方
                        # 記錄紅色框的四個角
                        red_box_points = [
                            (x, y),
                            (x + w, y),
                            (x + w, y + h),
                            (x, y + h)
                        ]
                        print(f"文字: {transcription}，紅色框四個角: {red_box_points}")

                        # 在圖片上繪製紅色框
                        draw.line([red_box_points[0], red_box_points[1], red_box_points[2], red_box_points[3], red_box_points[0]],
                                  fill=(255, 0, 0), width=2)

                        # 在框內添加文字（藍色）
                        text_x = red_box_points[0][0]
                        text_y = red_box_points[0][1] - 20  # 將文字放在框上方
                        draw.text((text_x, text_y), transcription, font=font, fill=(0, 0, 255, 255))

    except json.JSONDecodeError as e:
        print("JSON 解析失敗:", e)

# 將 PIL 圖片轉換回 OpenCV 圖片
image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

# 儲存結果圖片
output_path = 'output_with_red_boxes.jpg'
cv2.imwrite(output_path, image)
print(f"結果已儲存為 {output_path}")