import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import io

#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      APP 页面设置！必须炸裂！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
st.set_page_config(
    page_title="图片转话术 - 超级升级版!",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      APP 的无敌界面！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
st.title("📸 图片转酒店话术 - IShowSpeed看了都说YES! 🔥")
st.header("上传你的截图，AI 帮你生成话术！太酷啦！😎")

st.sidebar.header("⚙️ 上传你的截图！")
uploaded_file = st.sidebar.file_uploader("选择你的截图文件 (支持 JPG, PNG 等)", type=["jpg", "jpeg", "png"])

st.sidebar.subheader("✨ 话术选项")
default_group_type = st.selectbox("默认团队类型 (如果图片里没有)", ["会议团 (CON)", "散客团 (FIT)", "旅游团"], index=0)

st.sidebar.info("提示: 截图越清晰，识别效果越好哦！")

#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      核心逻辑！读取图片，识别文字！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
st.divider()
st.subheader("🚀 生成的话术在这里！")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="你上传的图片", use_column_width=True)

    st.info("正在识别图片中的文字... 请稍候！")
    try:
        # 使用 pytesseract 识别图片中的文字
        extracted_text = pytesseract.image_to_string(image, lang='chi_sim') # 尝试识别中文
        if not extracted_text.strip():
            extracted_text = pytesseract.image_to_string(image) # 如果中文识别失败，尝试识别英文等

        st.subheader("识别到的文字:")
        st.code(extracted_text)

        # --- 尝试从识别到的文字中提取信息 ---
        lines = extracted_text.strip().split('\n')
        group_name_from_image = ""
        check_in_from_image = ""
        check_out_from_image = ""
        room_data_from_image = []

        # 这里需要根据你的截图格式进行更智能的解析
        # 这只是一个非常基础的示例，你需要根据你的截图格式进行调整！
        first_line = lines and lines[-1] # 假设最后一行可能包含关键信息

        if lines:
            for line in lines:
                if "CON" in line or "FIT" in line:
                    parts = line.split()
                    for part in parts:
                        if "CON" in part or "FIT" in part:
                            group_name_from_image = part
                            break
                    break
            
            # 尝试查找日期，这部分可能需要更精确的匹配
            import re
            date_pattern = re.compile(r'(\d{2}/\d{2})')
            dates = date_pattern.findall(extracted_text)
            if len(dates) >= 2:
                check_in_guess = dates[-2].replace('/', '')
                check_out_guess = dates[-1].replace('/', '')
                if len(check_in_guess) == 4 and len(check_out_guess) == 4:
                    check_in_from_image = check_in_guess
                    check_out_from_image = check_out_guess

            # 尝试查找房间信息，这部分非常依赖截图格式
            for line in lines:
                if "SQS" in line or "SQN" in line or "SKN" in line or "STN" in line or "ETN" in line or "JKN" in line:
                    parts = line.split()
                    room_info = {}
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            room_info['count'] = part
                        elif part.isalpha() and len(part) >= 3:
                            room_info['type'] = part.upper()
                        elif i + 1 < len(parts) and parts [i+1].replace('.', '', 1).isdigit(): # 尝试找价格
                            room_info['price'] = parts [i+1]
                    if 'count' in room_info and 'type' in room_info and 'price' in room_info:
                        room_data_from_image.append(f"{room_info['count']}{room_info['type']}{room_info['price']}")


        # --- 生成最终话术 ---
        final_group_name = group_name_from_image if group_name_from_image else "未知团队"
        final_check_in = check_in_from_image if check_in_from_image else "XXXX"
        final_check_out = check_out_from_image if check_out_from_image else "XXXX"
        final_room_string = " ".join(room_data_from_image) if room_data_from_image else "没有识别到房间信息"
        final_group_type = default_group_type.split(" ")[0] if "未知团队" in final_group_name else default_group_type.split(" ")[0]

        if "没有识别到房间信息" not in final_room_string and final_check_in != "XXXX" and final_check_out != "XXXX" and "未知团队" not in final_group_name:
            final_script = f"新增{final_group_type} {final_group_name} {final_check_in}-{final_check_out} {final_room_string} 销售"
            st.subheader("✨ 自动生成的话术:")
            st.code(final_script, language="text")
            st.balloons()
        else:
            st.warning("⚠️ 无法完全自动生成话术。请检查识别到的文字，可能需要手动调整。")
            if final_check_in != "XXXX" and final_check_out != "XXXX":
                st.info(f"猜测日期: {final_check_in}-{final_check_out}")
            if final_group_name != "未知团队":
                st.info(f"猜测团队名称: {final_group_name}")
            if final_room_string != "没有识别到房间信息":
                st.info(f"猜测房间信息: {final_room_string}")


    except pytesseract.TesseractNotFoundError:
        st.error("😭 Tesseract OCR 未找到！请确保你已经安装了 Tesseract，并且添加到系统 PATH 环境变量中。")
    except Exception as e:
        st.error(f"识别图片时发生错误: {e}")
else:
    st.info("👆 请在侧边栏上传你的酒店订单截图！")
