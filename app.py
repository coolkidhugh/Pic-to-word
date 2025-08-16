import streamlit as st
import subprocess

st.set_page_config(page_title="Tesseract Health Check", layout="wide")
st.title("🩺 Tesseract 云端体检中心")
st.header("正在检查服务器上的 Tesseract OCR 环境...")

st.info("这个App的唯一目的，就是检查Tesseract在Streamlit Cloud上是否安装成功。")

# --- 检查 Tesseract 版本 ---
st.subheader("1. Tesseract 版本检查")
try:
    # 运行 tesseract --version 命令
    result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, check=True)
    st.text("命令: tesseract --version")
    st.code(result.stdout, language="text")
    st.success("✅ Tesseract 已安装！")
except FileNotFoundError:
    st.error("❌ Tesseract 命令未找到！这意味着 packages.txt 没有被正确处理，或者环境有问题。")
except Exception as e:
    st.error(f"❌ 运行版本检查时出错: {e}")
    st.code(e.stderr, language="text")

# --- 检查语言包 ---
st.subheader("2. 语言包检查")
try:
    # 运行 tesseract --list-langs 命令
    result = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True, check=True)
    st.text("命令: tesseract --list-langs")
    
    output_text = result.stdout
    if "chi_sim" in output_text:
        st.success("✅ 找到了简体中文语言包 (chi_sim)！")
    else:
        st.warning("⚠️ 未找到简体中文语言包 (chi_sim)！请确认 packages.txt 里写了 `tesseract-ocr-chi-sim`。")
    
    st.text_area("所有可用语言列表:", output_text, height=200)

except FileNotFoundError:
    st.error("❌ Tesseract 命令未找到！无法检查语言包。")
except Exception as e:
    st.error(f"❌ 运行语言检查时出错: {e}")
    st.code(e.stderr, language="text")

st.header("诊断报告")
st.write("请把上面的检查结果截图发给我，尤其是错误信息（如果有的话）。这样我们就能知道问题到底出在哪里了！")
