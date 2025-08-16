import streamlit as st
from PIL import Image
import requests
import base64
import io
import re

st.set_page_config(page_title="图片转话术 - v2.1 升序版", page_icon="🏆", layout="wide")
st.title("🏆 图片转话术 - v2.1 升序版! 🏆")

# --- 使用外部API进行OCR识别的函数 (保持不变) ---
def ocr_with_api(image_bytes):
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
# <<< 这里是核心升级！重构了解析和排序逻辑！>>>
#
def parse_ocr_text(text):
    group_name = "未知团队"
    check_in = "MMDD"
    check_out = "MMDD"
    rooms_list = [] # 改为使用列表存储字典，方便排序

    lines = text.strip().split('\n')

    # 1. 提取团队名称 (更稳健的逻辑)
    name_match = re.search(r'(CON\d+/[^\s\t]+)', text)
    if name_match:
        group_name = name_match.group(1).strip()

    # 2. 提取日期 (更稳健的逻辑)
    dates = re.findall(r'(\d{2}/\d{2})', text)
    unique_dates = sorted(list(set(dates)))
    if len(unique_dates) > 0:
        check_in = unique_dates[0].replace('/', '')
    if len(unique_dates) > 1:
        check_out = unique_dates[-1].replace('/', '')
    elif check_in != "MMDD":
        check_out = check_in

    # 3. 提取房间信息 (全新、更严格的逻辑)
    for line in lines:
        match = re.search(r'\b([A-Z]{3})\b\s+(\d{1,3})\s+.*\s+(\d{3,})', line)
        if match:
            room_type, count, price = match.groups()
            rooms_list.append({
                "type": room_type,
                "count": int(count),
                "price": int(price.replace('.00', ''))
            })

    # 4. 终极排序功能：按房数从小到大！
    # 删掉了 reverse=True，实现从小到大（升序）排列
    rooms_list.sort(key=lambda x: x['count'])

    # 5. 构建最终的话术字符串
    room_strings = [f"{room['count']}{room['type']}{room['price']}" for room in rooms_list]
    
    final_group_type = "会议团"
    if "FIT" in group_name:
        final_group_type = "散客团"

    return f"新增{final_group_type} {group_name} {check_in}-{check_out} {' '.join(room_strings)} 销售", len(room_strings) > 0


# --- 主界面 ---
st.header("上传截图，体验智能解析与从小到大排序！")
uploaded_file = st.file_uploader("上传你的截图文件", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # ... (这部分和之前一样，无需修改)
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_container_width=True)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    with st.spinner("正在调用 v2.1 大脑，进行智能解析和升序排序..."):
        try:
            extracted_text = ocr_with_api(img_byte_arr)
            st.subheader("🤖 v2.1 大脑识别出的原始文字:")
            st.text_area("原始文字", extracted_text, height=250)

            final_script, success = parse_ocr_text(extracted_text)
            st.subheader("✅ AI为你生成的最终话术 (已从小到大排序):")
            if success:
                st.code(final_script, language="text")
                st.balloons()
            else:
                st.warning("⚠️ 解析失败。请检查原始文字，可能是截图格式非常特殊。")
                st.code(final_script, language="text")
        except Exception as e:
            st.error(f"发生错误 bro！: {e}")
