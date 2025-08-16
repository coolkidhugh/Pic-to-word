import streamlit as st
from PIL import Image
import pytesseract
import re

#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      APP 页面设置！必须炸裂！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
st.set_page_config(
    page_title="图片转话术 - 史诗升级版!",
    page_icon="🧠",
    layout="wide"
)

#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      APP 的无敌界面！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
st.title("🧠 图片转酒店话术 - AI大脑升级版! 🔥")
st.header("上传截图，让更聪明的AI帮你生成话术！")

uploaded_file = st.sidebar.file_uploader(
    "上传你的截图文件 (PNG, JPG)", 
    type=["png", "jpg", "jpeg"]
)
st.sidebar.info("提示: 截图越清晰、裁剪越精准，AI识别成功率越高！")


#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      核心逻辑！更智能的解析！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
def parse_ocr_text(text):
    """
    使用更强大的正则表达式来解析混乱的OCR文本
    """
    group_name = "未知团队"
    check_in = "MMDD"
    check_out = "MMDD"
    rooms = []

    lines = text.strip().split('\n')

    # 1. 提取团队名称 (更模糊的匹配)
    for line in lines:
        if "CON" in line or "江苏省" in line or "江落省" in line:
            # 尝试从'/'分割，或者取包含CON的部分
            match = re.search(r'(CON\d+/[^ ]+)', line)
            if match:
                group_name = match.group(1)
            else: # 如果上面找不到，就用个备用方案
                parts = [p for p in line.split(' ') if p]
                if len(parts) > 1:
                    group_name = ' '.join(parts[1:3]) # 大胆猜测第二个和第三个部分是名字
            break
            
    # 2. 提取日期
    dates = re.findall(r'(\d{2}/\d{2})', text)
    if len(dates) >= 2:
        check_in = dates[0].replace('/', '')
        check_out = dates[1].replace('/', '')

    # 3. 提取房间信息 (最关键的升级)
    # 模式: 匹配一个3字母的代码，前后可能有数字
    # 例如: SQS 15 ... 550.00 或者 15 SQN ... 550.00
    for line in lines:
        # 寻找一个明确的3字母大写房型代码
        room_type_match = re.search(r'\b([A-Z]{3})\b', line)
        if room_type_match:
            room_type = room_type_match.group(1)
            
            # 在同一行里寻找数字，第一个通常是数量，最后一个通常是价格
            numbers = re.findall(r'(\d+)', line.replace('.00', '')) # 把.00去掉，方便匹配
            
            if len(numbers) >= 2:
                count = numbers[0]
                price = numbers[-1]
                # 简单的验证，防止把日期里的数字当成价格
                if int(price) > 100: 
                    rooms.append(f"{count}{room_type}{price}")

    final_group_type = "会议团" # 默认值
    if "FIT" in group_name:
        final_group_type = "散客团"

    return f"新增{final_group_type} {group_name} {check_in}-{check_out} {' '.join(rooms)} 销售", len(rooms) > 0


if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_container_width=True)

    with st.spinner("AI 大脑正在高速运转，识别中..."):
        try:
            # 使用中英文混合识别
            extracted_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            st.subheader("🤖 AI识别出的原始文字:")
            st.text_area("原始文字", extracted_text, height=200)

            final_script, success = parse_ocr_text(extracted_text)

            st.subheader("✨ AI为你生成的话术:")
            if success:
                st.code(final_script, language="text")
                st.balloons()
            else:
                st.warning("⚠️ AI尽力了，但信息可能不完整。请检查原始文字，手动修改下面的话术。")
                st.code(final_script, language="text")

        except Exception as e:
            st.error(f"发生了一个错误 bro！可能是 Tesseract 没装好: {e}")
else:
    st.info("👆 在左边上传截图，见证奇迹！")
