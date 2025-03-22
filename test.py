# 產生一個 Streamlit 範例程式   好好測試

from openocr import OpenOCR
import json  # 用於解析 JSON 格式的資料

engine = OpenOCR()
img_path = 'oo1.jpg'
result= engine(img_path)

# 打印 result 的結構
print("Result 的類型:", type(result))
print("Result 的內容:", result)

# 處理第一部分：解析 JSON 格式的字串
if len(result) > 0 and isinstance(result[0], list):
    json_string = result[0][0]  # 取出第一部分的字串
   #print("第一部分的內容:", json_string)

    # 將 JSON 格式的字串轉換為 Python 資料結構
    try:
        parsed_data = json.loads(json_string.split("\t")[1])  # 提取 JSON 部分並解析
        for item in parsed_data:
            transcription = item.get("transcription", "無法取得 transcription")
            points = item.get("points", "無法取得 points")
            score = item.get("score", "無法取得 score")
            print(f"識別內容: {transcription}, 區域: {points}, 信心分數: {score}")
    except json.JSONDecodeError as e:
        print("JSON 解析失敗:", e)

# 處理第二部分：時間相關的字典
if len(result) > 1 and isinstance(result[1], list):
    time_data = result[1][0]  # 取出時間相關的字典
    if isinstance(time_data, dict):
        print("第二部分的內容:")
        for key, value in time_data.items():
            print(f"{key}: {value}")