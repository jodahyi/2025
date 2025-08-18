import streamlit as st

# =====================
# Page Setup
# =====================
st.set_page_config(
    page_title="🎨 색채 심리 테스트",
    page_icon="🖌️",
    layout="centered"
)

st.title("🎨 나의 색채 심리 테스트")
st.markdown("좋아하는 색을 선택하면 당신의 성격과 디자인 취향을 알려줍니다.")

# =====================
# 색상 데이터
# =====================
color_data = {
    "빨강": {
        "hex": "#E53935",
        "desc": "열정적이고 용기 있는 성격으로 도전과 경쟁을 즐깁니다. 리더십이 강하고 주변 사람들에게 활력을 줍니다.",
        "design": "강렬한 대비와 눈에 띄는 포인트 컬러를 활용한 디자인을 선호합니다."
    },
    "파랑": {
        "hex": "#1E88E5",
        "desc": "차분하고 신중하며 이성적인 판단을 중요시합니다. 안정과 신뢰를 중시하고 계획적으로 움직이는 성격입니다.",
        "design": "깔끔하고 정돈된 레이아웃, 미니멀한 디자인을 좋아합니다."
    },
    "노랑": {
        "hex": "#FDD835",
        "desc": "긍정적이고 명랑하며 창의적입니다. 새로운 아이디어를 내는 것을 좋아하고, 사교적이며 낙천적인 성격입니다.",
        "design": "밝고 활기찬 색상, 경쾌한 패턴 디자인을 선호합니다."
    },
    "초록": {
        "hex": "#43A047",
        "desc": "조화롭고 안정적인 성격으로 자연과 균형을 중요시합니다. 평화로운 분위기를 좋아하며 감정이 안정적입니다.",
        "design": "자연의 색감을 살린 부드러운 디자인, 편안한 톤을 선호합니다."
    },
    "보라": {
        "hex": "#8E24AA",
        "desc": "예술적 감각이 뛰어나고 창의적입니다. 감성적이며 독창적인 생각을 즐기고, 자신만의 세계관을 중요하게 여깁니다.",
        "design": "독창적이고 예술적인 패턴, 유니크한 디자인을 선호합니다."
    },
    "검정": {
        "hex": "#212121",
        "desc": "신비롭고 세련된 이미지를 선호합니다. 집중력이 높고 자기 주장이 뚜렷하며, 정리정돈과 모던한 스타일을 좋아합니다.",
        "design": "모던하고 깔끔한 디자인, 고급스러운 느낌을 주는 색상을 선호합니다."
    },
    "흰색": {
        "hex": "#FAFAFA",
        "desc": "순수하고 깔끔하며 정리정돈을 중시합니다. 마음이 평온하고 객관적이며 새로운 시작을 좋아합니다.",
        "design": "깔끔하고 미니멀한 디자인, 밝고 정돈된 색감을 선호합니다."
    }
}

# =====================
# 색상 선택 UI
# =====================
st.markdown("### 좋아하는 색을 선택하세요:")

selected_color = st.session_state.get("selected_color", None)

cols = st.columns(len(color_data))
for i, (color_name, info) in enumerate(color_data.items()):
    if st.button(
        color_name,
        key=color_name,
        help="클릭하면 결과가 표시됩니다.",
        args=None
    ):
        selected_color = color_name
        st.session_state["selected_color"] = color_name

    # CSS 스타일 적용: 실제 색 배경 + 강조 효과
    st.markdown(
        f"""
        <style>
        div.stButton > button:contains("{color_name}") {{
            background-color: {info['hex']};
            color: {"#FFFFFF" if color_name != "노랑" else "#000000"};
            border-radius: 12px;
            height: 60px;
            font-size: 16px;
            font-weight: bold;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================
# 결과 출력
# =====================
if selected_color:
    info = color_data[selected_color]
    st.markdown(f"## 🎯 당신이 선택한 색: {selected_color}")
    st.markdown(f"**성격 특징:** {info['desc']}")
    st.markdown(f"**디자인 취향:** {info['design']}")
