import streamlit as st
from PIL import Image
import requests
import base64
import io
import re

st.set_page_config(page_title="图片转话术 - 最终版", page_icon="🏆", layout="wide")
st.title("🏆 图片转话术 - 最终BOSS战版! 🏆")

# --- 使用外部API进行OCR识别的函数 (增加了表格识别指令!) ---
def ocr_with_api(image_bytes):
    API_URL = "https://api.ocr.space/parse/image"
    API_KEY = "helloworld" # 使用公共测试key

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        'apikey': API_KEY,
        'language': 'chs',          # 语言：简体中文
        'isOverlayRequired': False,
        'base64Image': f'data:image/png;base64,{base64_image}',
        #
        # <<< 这里是关键升级！我们告诉AI这是一个表格！>>>
        #
        'isTable': True,            # 启用表格识别模式！
        'scale': True               # 允许API自动缩放图片以获得最佳效果
    }
    
    response = requests.post(API_URL, data=payload)
    response.raise_for_status()
    
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        raise Exception(f"API处理错误: {result.get('ErrorMessage')}")
        
    # 在表格模式下，文本在TextOverlay.Lines中
    parsed_text = ""
    for r in result['ParsedResults']:
        parsed_text += r['ParsedText']

    return parsed_text


# --- 解析文本的函数 (保持不变，因为它很强了) ---
def parse_ocr_text(text):
    group_name = "未知团队"
    check_in = "MMDD"
    check_out = "MMDD"
    rooms = []
    lines = text.strip().split('\n')

    # 1. 提取团队名称
    for line in lines:
        if "CON" in line and "江苏省" in line:
            # 使用更精确的匹配来提取干净的团队名称
            match = re.search(r'(CON\d+/\S+)', line)
            if match:
                group_name = match.group(1).strip()
                break

    # 2. 提取日期
    dates = re.findall(r'(\d{2}/\d{2})', text)
    unique_dates = sorted(list(set(dates)))
    if len(unique_dates) >= 2:
        check_in = unique_dates[0].replace('/', '')
        check_out = unique_dates[-1].replace('/', '') # 取最后一个作为离店日期

    # 3. 提取房间信息
    for line in lines:
        # 模式: 必须包含一个三字母房型 和 至少两个数字 (房数和价格)
        room_type_match = re.search(r'\b([A-Z]{3})\b', line)
        numbers_match = re.findall(r'(\d{2,})', line.replace('.00', '')) # 匹配两位及以上的数字
        
        if room_type_match and len(numbers_match) >= 2:
            room_type = room_type_match.group(1)
            # 假设第一个数字是房数，最后一个是价格
            count = numbers_match[0]
            price = numbers_match[-1]
            rooms.append(f"{count}{room_type}{price}")

    final_group_type = "会议团"
    if "FIT" in group_name:
        final_group_type = "散客团"
        
    # 去重房间信息
    unique_rooms = sorted(list(set(rooms)))

    return f"新增{final_group_type} {group_name} {check_in}-{check_out} {' '.join(unique_rooms)} 销售", len(unique_rooms) > 0


# --- 主界面 ---
st.header("上传截图，这是最后一战！")
uploaded_file = st.file_uploader("上传你的截图文件", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_container_width=True)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    with st.spinner("正在调用终极AI大脑，并开启表格模式..."):
        try:
            extracted_text = ocr_with_api(img_byte_arr)
            st.subheader("🤖 终极AI (表格模式) 识别出的原始文字:")
            st.text_area("原始文字", extracted_text, height=250)

            final_script, success = parse_ocr_text(extracted_text)
            st.subheader("✨ AI为你生成的最终话术:")
            if success:
                st.code(final_script, language="text")
                st.balloons()
            else:
                st.warning("⚠️ 识别成功，但信息可能不完整。请检查原始文字并手动调整话术。")
                st.code(final_script, language="text")

        except Exception as e:
            st.error(f"调用终极AI时发生错误 bro！: {e}")
