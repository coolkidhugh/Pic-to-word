import streamlit as st
from PIL import Image
import requests
import base64
import io
import re

st.set_page_config(page_title="图片转话术 - v3.0 最终版", page_icon="👑", layout="wide")
st.title("👑 图片转话术 - v3.0 最终版! 👑")

# --- OCR API调用函数 (保持不变) ---
def ocr_with_api(image_bytes):
    API_URL = "https://api.ocr.space/parse/image"
    API_KEY = "helloworld" # 建议换成你自己的免费Key
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        'apikey': API_KEY, 'language': 'chs', 'isOverlayRequired': False,
        'base64Image': f'data:image/png;base64,{base64_image}',
        'isTable': True, 'scale': True
    }
    response = requests.post(API_URL, data=payload)
    response.raise_for_status()
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        raise Exception(f"API处理错误: {result.get('ErrorMessage')}")
    parsed_text = ""
    for r in result['ParsedResults']:
        parsed_text += r['ParsedText']
    return parsed_text

#
# <<< 核心！v3.0版的全新解析大脑！>>>
#
def parse_ocr_text(text):
    # 预处理：清理常见的OCR错误
    text = text.replace('〕', 'O').replace('．', '.').replace('引', '6')

    group_name = "未知团队"
    check_in = "MMDD"
    check_out = "MMDD"
    rooms_list = []

    lines = text.strip().split('\n')

    # 1. 提取团队名称 (更强大的模糊匹配)
    # 匹配类似 CON25359/... 的格式，对CON的识别错误有一定容错
    name_match = re.search(r'([A-Z0-9]{2,4}\d{5}/[^\s\t]+)', text, re.IGNORECASE)
    if name_match:
        group_name = name_match.group(1).strip()

    # 2. 提取日期
    dates = re.findall(r'(\d{2}/\d{2})', text)
    unique_dates = sorted(list(set(dates)))
    if len(unique_dates) > 0:
        check_in = unique_dates[0].replace('/', '')
    if len(unique_dates) >= 1: # 即使只有一个日期也用它
        check_out = unique_dates[-1].replace('/', '')

    # 3. 提取房间信息 (全新！更稳健的列式解析逻辑)
    for line in lines:
        # 模式解释:
        # ([A-Z]{3})      -> 捕获一个三字母的房型 (例如 SQS)
        # \s+             -> 至少一个空格
        # (\d{1,3})       -> 捕获1到3位的房数 (例如 10)
        # .*?             -> 非贪婪匹配中间的所有字符
        # (\d{3,})\.\d{2} -> 捕获一个像价格的数字 (例如 630.00)
        match = re.search(r'([A-Z]{3})\s+(\d{1,3})\s+.*?\s+(\d{3,})\.\d{2}', line)
        
        if match:
            room_type, count, price = match.groups()
            rooms_list.append({
                "type": room_type,
                "count": int(count),
                "price": int(price)
            })

    # 4. 排序 (从小到大)
    rooms_list.sort(key=lambda x: x['count'])

    # 5. 构建话术
    room_strings = [f"{room['count']}{room['type']}{room['price']}" for room in rooms_list]
    
    final_group_type = "会议团"
    if "FIT" in group_name:
        final_group_type = "散客团"

    return f"新增{final_group_type} {group_name} {check_in}-{check_out} {' '.join(room_strings)} 销售", len(room_strings) > 0


# --- 主界面 (保持不变) ---
st.header("上传截图，体验v3.0智能大脑！")
uploaded_file = st.file_uploader("上传你的截图文件", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_container_width=True)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    with st.spinner("正在调用v3.0终极大脑..."):
        try:
            extracted_text = ocr_with_api(img_byte_arr)
            st.subheader("🤖 v3.0 大脑识别出的原始文字:")
            st.text_area("原始文字", extracted_text, height=250)

            final_script, success = parse_ocr_text(extracted_text)
            st.subheader("✅ AI为你生成的最终话术 (已排序):")
            if success:
                st.code(final_script, language="text")
                st.balloons()
            else:
                st.warning("⚠️ 解析失败。请检查原始文字，可能是截图格式非常特殊。")
                st.code(final_script, language="text")
        except Exception as e:
            st.error(f"发生错误 bro！: {e}")
