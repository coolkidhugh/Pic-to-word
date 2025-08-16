import streamlit as st
from PIL import Image
import requests
import base64
import io
import re

st.set_page_config(page_title="图片转话术 - 毕业版", page_icon="🎓", layout="wide")
st.title("🎓 图片转话术 - 毕业版 (AI初稿 + 手动修正)")

# --- OCR API调用函数 (保持不变) ---
def ocr_with_api(image_bytes):
    API_URL = "https://api.ocr.space/parse/image"
    API_KEY = "helloworld" # 建议换成你自己的免费Key
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    payload = { 'apikey': API_KEY, 'language': 'chs', 'isOverlayRequired': False,
        'base64Image': f'data:image/png;base64,{base64_image}', 'isTable': True, 'scale': True }
    response = requests.post(API_URL, data=payload)
    response.raise_for_status()
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        raise Exception(f"API处理错误: {result.get('ErrorMessage')}")
    parsed_text = ""
    for r in result['ParsedResults']: parsed_text += r['ParsedText']
    return parsed_text

# --- 解析文本的函数 (保持v4.0的强大逻辑) ---
def parse_ocr_text(text):
    text = text.replace('〕', 'O').replace('．', '.').replace('引', '6').replace('H', 'N').replace('0N', 'CON')
    group_name = "未知团队"
    check_in, check_out = "MMDD", "MMDD"
    rooms_list = []
    lines = text.strip().split('\n')
    name_match = re.search(r'(CON\d+/[^\s\t]+)', text, re.IGNORECASE)
    if name_match: group_name = name_match.group(1).strip()
    dates = re.findall(r'(\d{2}/\d{2})', text)
    unique_dates = sorted(list(set(dates)))
    if len(unique_dates) > 0: check_in = unique_dates[0].replace('/', '')
    if len(unique_dates) >= 1: check_out = unique_dates[-1].replace('/', '')
    for line in lines:
        match = re.search(r'([A-Z]{3})\s+(\d{1,3})\s+.*?\s+(\d{3,})\.\d{2}', line)
        if match:
            room_type, count, price = match.groups()
            rooms_list.append({"type": room_type, "count": int(count), "price": int(price)})
    rooms_list.sort(key=lambda x: x['count'])
    room_strings = [f"{room['count']}{room['type']}{room['price']}" for room in rooms_list]
    final_group_type = "会议团"
    if "FIT" in group_name: final_group_type = "散客团"
    return f"新增{final_group_type} {group_name} {check_in}-{check_out} {' '.join(room_strings)} 销售", len(room_strings) > 0

# --- 主界面 ---
st.header("1. 上传你的截图")
uploaded_file = st.file_uploader("点击这里选择图片", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_container_width=True)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    with st.spinner("正在调用AI大脑进行初步识别..."):
        try:
            # 首次识别
            if 'ocr_text' not in st.session_state or st.session_state.get('uploaded_file_name') != uploaded_file.name:
                st.session_state.ocr_text = ocr_with_api(img_byte_arr)
                st.session_state.uploaded_file_name = uploaded_file.name

            st.header("2. 检查并修正AI识别的文字")
            st.info("如果下面的文字有错（比如房数不对），直接在文本框里手动改掉就行了！")
            
            # 可编辑的文本框
            corrected_text = st.text_area("可编辑的原始文字:", st.session_state.ocr_text, height=250)
            
            # 使用修正后的文本生成话术
            final_script, success = parse_ocr_text(corrected_text)

            st.header("3. 复制最终的完美话术")
            st.code(final_script, language="text")
            if success:
                st.success("生成成功！如果结果不对，请修正上面的文字，话术会自动更新。")
            else:
                st.warning("部分信息解析失败，请检查并修正上面的原始文字。")

        except Exception as e:
            st.error(f"发生错误 bro！: {e}")
