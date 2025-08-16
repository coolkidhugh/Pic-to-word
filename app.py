import streamlit as st
from PIL import Image
import requests
import base64
import io
import re

st.set_page_config(page_title="图片转话术 - v4.0 最终版", page_icon="👑", layout="wide")
st.title("👑 图片转话术 - v4.0 最终版! 👑")

def ocr_with_api(image_bytes):
    # ... (这部分和之前一样，无需修改)
    API_URL = "https://api.ocr.space/parse/image"
    API_KEY = "helloworld"
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
# <<< 核心！v4.0版的全新解析大脑！>>>
#
def parse_ocr_text(text):
    # 预处理：清理常见的OCR错误
    text = text.replace('〕', 'O').replace('．', '.').replace('引', '6').replace('H', 'N').replace('0N', 'CON')

    group_name = "未知团队"
    check_in = "MMDD"
    check_out = "MMDD"
    rooms_list = []

    lines = text.strip().split('\n')

    # 1. 提取团队名称 (更强大的模糊匹配)
    name_match = re.search(r'(CON\d+/[^\s\t]+)', text, re.IGNORECASE)
    if name_match:
        group_name = name_match.group(1).strip()

    # 2. 提取日期
    dates = re.findall(r'(\d{2}/\d{2})', text)
    unique_dates = sorted(list(set(dates)))
    if len(unique_dates) > 0:
        check_in = unique_dates[0].replace('/', '')
    if len(unique_dates) >= 1:
        check_out = unique_dates[-1].replace('/', '')

    # 3. 提取房间信息 (v4.0 全新容错逻辑)
    for line in lines:
        room_type = ""
        count = ""
        price = ""
        
        # 步骤A: 锁定房型和它旁边的房数，这是最关键的组合
        type_count_match = re.search(r'([A-Z]{3})\s+(\d{1,3})', line)
        if type_count_match:
            room_type, count = type_count_match.groups()

            # 步骤B: 在这行的末尾寻找价格
            price_match = re.search(r'(\d{3,})', line.split(count)[-1]) # 只在房数后面的文本里找价格
            if price_match:
                price = price_match.group(1)
        
        # 只有三个关键信息都找到，才算成功
        if room_type and count and price:
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
st.header("上传截图，体验v4.0智能大脑！")
# ... (后面的UI部分和之前完全一样，无需修改)
uploaded_file = st.file_uploader("上传你的截图文件", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_container_width=True)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    with st.spinner("正在调用v4.0终极大脑..."):
        try:
            extracted_text = ocr_with_api(img_byte_arr)
            st.subheader("🤖 v4.0 大脑识别出的原始文字:")
            st.text_area("原始文字", extracted_text, height=250)

            final_script, success = parse_ocr_text(extracted_text)
            st.subheader("✅ AI为你生成的最终话术 (已排序):")
            if success:
                st.code(final_script, language="text")
                st.balloons()
            else:
                st.warning("⚠️ 解析失败。请检查原始文字，可能有部分信息OCR未能识别。")
                st.code(final_script, language="text")
        except Exception as e:
            st.error(f"发生错误 bro！: {e}")
