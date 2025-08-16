import streamlit as st
from PIL import Image
import requests # 我们需要这个库来调用外部API
import base64
import io
import re

st.set_page_config(page_title="图片转话术 - 核动力版", page_icon="☢️", layout="wide")
st.title("☢️ 图片转话术 - 核动力版! 🔥")

# --- 使用外部API进行OCR识别的函数 ---
def ocr_with_api(image_bytes):
    # 这是一个免费的公共OCR API端点，用来进行测试
    # 注意：请勿在生产环境或处理敏感信息时使用公共API
    API_URL = "https://api.ocr.space/parse/image"
    # 你可以免费在这里获取自己的API Key: https://ocr.space/
    API_KEY = "helloworld" # 这是一个测试用的key，可能会有限制

    # 将图片字节转换为base64编码的字符串
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        'apikey': API_KEY,
        'language': 'chs', # chs 代表简体中文
        'isOverlayRequired': False,
        'base64Image': f'data:image/png;base64,{base64_image}'
    }
    
    response = requests.post(API_URL, data=payload)
    response.raise_for_status() # 如果请求失败则抛出异常
    
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        raise Exception(f"API处理错误: {result.get('ErrorMessage')}")
        
    return result['ParsedResults'][0]['ParsedText']


# --- 解析文本的函数 (跟之前一样) ---
def parse_ocr_text(text):
    group_name = "未知团队"
    check_in = "MMDD"
    check_out = "MMDD"
    rooms = []
    lines = text.strip().split('\n')
    for line in lines:
        if "CON" in line or "江苏省" in line:
            match = re.search(r'(CON\d+/[^\s\t]+)', line)
            if match:
                group_name = match.group(1)
            break
    dates = re.findall(r'(\d{2}/\d{2})', text)
    if len(dates) >= 2:
        check_in = dates[0].replace('/', '')
        check_out = dates[1].replace('/', '')
    for line in lines:
        room_type_match = re.search(r'\b([A-Z]{3})\b', line)
        if room_type_match:
            room_type = room_type_match.group(1)
            numbers = re.findall(r'(\d+)', line.replace('.00', ''))
            if len(numbers) >= 2:
                count, price = (numbers[0], numbers[-1]) if len(numbers[0]) < 3 else (numbers[1], numbers[-1])
                if int(price) > 100:
                    rooms.append(f"{count}{room_type}{price}")
    final_group_type = "会议团"
    if "FIT" in group_name:
        final_group_type = "散客团"
    return f"新增{final_group_type} {group_name} {check_in}-{check_out} {' '.join(rooms)} 销售", len(rooms) > 0


# --- 主界面 ---
st.header("上传截图，调用超级AI大脑！")
uploaded_file = st.file_uploader("上传你的截图文件", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_container_width=True)

    # 将图片转换为字节流
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    with st.spinner("正在调用外部超级AI大脑..."):
        try:
            # 调用外部API
            extracted_text = ocr_with_api(img_byte_arr)
            st.subheader("🤖 超级AI识别出的原始文字:")
            st.text_area("原始文字", extracted_text, height=200)

            final_script, success = parse_ocr_text(extracted_text)
            st.subheader("✨ AI为你生成的话术:")
            if success:
                st.code(final_script, language="text")
                st.balloons()
            else:
                st.warning("⚠️ 识别成功，但信息可能不完整。请检查原始文字并手动调整话术。")
                st.code(final_script, language="text")

        except Exception as e:
            st.error(f"调用超级AI时发生错误 bro！: {e}")
