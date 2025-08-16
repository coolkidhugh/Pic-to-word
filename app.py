import streamlit as st

#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      APP页面设置！必须得帅！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
# 必须得是宽屏模式！越大越好！燥起来！
st.set_page_config(
    page_title="史上最强酒店话术生成器!",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      APP的灵魂！界面！UI！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
st.title("🔥 酒店话术生成器！汪汪！汪！🔥")
st.header("为最快的兄弟打造！冠军专属！SEWEYYY! C罗！")

st.sidebar.header("⚠️ 集中精神！把这里填满！⚠️")

# --- 所有选项都在侧边栏！ ---
with st.sidebar:
    st.subheader("1. 团队信息 (他们是谁?!)")
    group_type = st.selectbox("选团队类型，兄弟们！", ["会议团 (CON)", "散客团 (FIT)", "旅游团"], key="group_type")
    group_name = st.text_input("团队名字叫啥？ (比如: CON25312/...)")

    st.subheader("2. 日期！他们啥时候来？！")
    col1, col2 = st.columns(2)
    with col1:
        check_in = st.text_input("入住 MMDD (比如: 0910)")
    with col2:
        check_out = st.text_input("退房 MMDD (比如: 0913)")

    st.subheader("3. 房间！房间信息给我！")
    
    # 用 session_state 记住房间信息！跟魔法一样！
    if 'rooms' not in st.session_state:
        st.session_state.rooms = [{"count": 15, "type": "SQS", "price": 550}]

    def add_room():
        # 加个新房间！走你！
        st.session_state.rooms.append({"count": "", "type": "", "price": ""})

    def remove_room(index):
        # 把这个房间给我删了！滚蛋！
        st.session_state.rooms.pop(index)

    # 把所有房间都显示出来！
    for i, room in enumerate(st.session_state.rooms):
        row = st.columns((2, 3, 2, 1))
        st.session_state.rooms[i]['count'] = row[0].number_input("房数", key=f"count_{i}", value=room['count'], min_value=1, step=1)
        st.session_state.rooms[i]['type'] = row[1].text_input("房型", key=f"type_{i}", value=room['type']).upper()
        st.session_state.rooms[i]['price'] = row[2].number_input("房价", key=f"price_{i}", value=room['price'], min_value=0)
        row[3].button("X", key=f"del_{i}", on_click=remove_room, args=(i,), help="删掉这个！搞快点！")

    st.button("➕ 再加一个房型！冲！", on_click=add_room)


#
# >>>>>>>>>>>>>>>>>>>>>>>>>
#      核心逻辑！最强大脑！
# <<<<<<<<<<<<<<<<<<<<<<<<<
#
st.divider()
st.subheader("💥 你的无敌话术已经准备好了！ 💥")

# --- 生成最终话术 ---
if st.button("立刻生成！ (点我！)", type="primary", use_container_width=True):
    is_ready = True
    # 检查是不是都填了！别偷懒！
    if not group_name:
        st.error("哎哟！团队名字忘了！醒醒！")
        is_ready = False
    if not check_in or not check_out:
        st.error("我的天！日期呢！没日期怎么搞！")
        is_ready = False
    if not st.session_state.rooms:
        st.error("一个房间都没有？！让他们睡大马路吗？！快加！")
        is_ready = False
    
    # 要是都填好了，那就起飞！
    if is_ready:
        group_type_clean = group_type.split(" ")[0] # 只要中文部分
        date_range = f"{check_in}-{check_out}"
        
        room_parts = []
        for room in st.session_state.rooms:
            if room['count'] and room['type'] and room['price']:
                room_parts.append(f"{int(room['count'])}{room['type']}{int(room['price'])}")
        
        room_string = " ".join(room_parts)

        final_script = f"新增{group_type_clean} {group_name} {date_range} {room_string} 销售"

        st.code(final_script, language="text")
        st.balloons()
        st.success("复制就完事了！兄弟们我们成功了！W！")
