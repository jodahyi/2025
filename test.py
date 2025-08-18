import streamlit as st

# =====================
# Page Setup
# =====================
st.set_page_config(
    page_title="🎨 색채 심리 테스트",
    page_icon="🖌️",
    layout="wide"
)

st.title("🎨 나의 색채 심리 테스트")
st.markdown("좋아하는 색을 선택하면 심리적 특성, 성격 유형, 디자인 취향, 학습 스타일, 직업 적합성까지 알려줍니다.")

# =====================
# 색상 데이터
# =====================
color_data = {
    "빨강": {"hex":"#E53935", "desc":"강렬한 열정과 에너지를 가지고 있으며, 모험과 도전을 즐깁니다. 대담하고 리더십이 강합니다.",
             "design":"강렬한 대비와 포인트 색상, 역동적 디자인 선호",
             "learning":"행동 중심, 실습과 활동형 학습 선호",
             "career":"리더, 마케팅, 운동선수, 창의적 프로젝트 적합"},
    "주황": {"hex":"#FB8C00", "desc":"밝고 사교적이며 창의력이 풍부합니다. 팀워크를 즐기고 주변 사람들과 소통을 좋아합니다.",
             "design":"활기찬 색상과 재미있는 패턴 디자인 선호",
             "learning":"그룹 학습과 아이디어 공유형 학습 선호",
             "career":"광고, 이벤트, 기획, 교육 관련 직업 적합"},
    "노랑": {"hex":"#FDD835", "desc":"낙천적이고 호기심이 많으며 창의적인 사고를 즐깁니다. 명랑하고 긍정적입니다.",
             "design":"밝고 경쾌한 색상, 눈에 띄는 디자인 선호",
             "learning":"관찰과 실험 중심 학습 선호",
             "career":"디자이너, 예술가, 강사, 창의적 직업 적합"},
    "초록": {"hex":"#43A047", "desc":"조화롭고 안정적인 성격으로 감정이 안정적입니다. 자연과 균형을 중요시합니다.",
             "design":"자연색, 부드러운 톤과 편안한 디자인 선호",
             "learning":"계획적, 집중 학습 선호",
             "career":"환경, 치유, 자연 관련 직업 적합"},
    "파랑": {"hex":"#1E88E5", "desc":"차분하고 신중하며 분석적입니다. 안정과 신뢰를 중요시합니다.",
             "design":"정돈된 레이아웃과 미니멀 디자인 선호",
             "learning":"분석적, 자료 정리 중심 학습 선호",
             "career":"연구, 공학, IT, 관리 직무 적합"},
    "보라": {"hex":"#8E24AA", "desc":"예술적 감각이 뛰어나고 창의적입니다. 독창적이고 감성적인 사고를 선호합니다.",
             "design":"독창적이고 예술적인 패턴과 디자인 선호",
             "learning":"창의적 프로젝트 중심 학습 선호",
             "career":"예술, 디자인, 창작 직업 적합"},
    "분홍": {"hex":"#EC407A", "desc":"사교적이고 다정하며 감성적입니다. 타인과 소통과 배려를 중요시합니다.",
             "design":"부드럽고 로맨틱한 색상과 디자인 선호",
             "learning":"협동 학습 및 소통 중심 학습 선호",
             "career":"교육, 상담, 서비스 관련 직업 적합"},
    "청록": {"hex":"#00ACC1", "desc":"논리적이면서도 차분하고 독창적인 성향이 있습니다.",
             "design":"현대적이고 깔끔한 톤의 디자인 선호",
             "learning":"분석과 관찰 중심 학습 선호",
             "career":"연구, IT, 디자인 직업 적합"},
    "갈색": {"hex":"#6D4C41", "desc":"현실적이고 신뢰할 수 있는 성격입니다. 안정감과 성실함을 중요시합니다.",
             "design":"내추럴 톤, 편안하고 안정적인 디자인 선호",
             "learning":"체계적, 반복 학습 스타일",
             "career":"관리, 회계, 교육, 자연 관련 직업 적합"},
    "검정": {"hex":"#212121", "desc":"신비롭고 세련된 이미지를 선호하며 집중력과 자기주장이 강합니다.",
             "design":"모던, 심플, 고급스러운 디자인 선호",
             "learning":"집중적 자기주도 학습 선호",
             "career":"디자인, 예술, 기획, 전략적 직무 적합"},
    "흰색": {"hex":"#FAFAFA", "desc":"순수하고 깔끔하며 평화를 중시합니다. 객관적이고 새로운 시작을 좋아합니다.",
             "design":"깔끔하고 정돈된 디자인 선호",
             "learning":"정리와 계획 중심 학습 선호",
             "career":"교육, 연구, 기획, 상담 직업 적합"},
    "회색": {"hex":"#9E9E9E", "desc":"중립적이고 분석적이며 침착합니다. 감정을 안정적으로 유지합니다.",
             "design":"차분하고 절제된 디자인 선호",
             "learning":"논리적, 분석적 학습 선호",
             "career":"IT, 분석, 회계, 관리 직무 적합"}
}

# =====================
# 선택 UI (항상 표시)
# =====================
st.markdown("### 좋아하는 색을 선택하세요:")
selected_color = st.session_state.get("selected_color", None)
cols = st.columns(4)

for i, (color_name, info) in enumerate(color_data.items()):
    with cols[i % 4]:
        if st.button(color_name):
            st.session_state["selected_color"] = color_name
            selected_color = color_name

        # 버튼 스타일
        st.markdown(f"""
        <style>
        div.stButton > button:contains("{color_name}") {{
            background-color: {info['hex']};
            color: {"#000000" if color_name in ['노랑','청록','주황'] else "#FFFFFF"};
            border-radius: 12px;
            height: 60px;
            font-size: 16px;
            font-weight: bold;
        }}
        </style>
        """, unsafe_allow_html=True)

# =====================
# 결과 표시 (선택 후)
# =====================
if selected_color:
    info = color_data[selected_color]

    # 페이지 배경 변경
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {info['hex']};
        color: {"#000000" if selected_color in ['노랑','청록','주황'] else "#FFFFFF"};
    }}
    </style>
    """, unsafe_allow_html=True)

    # 카드형 결과
    st.markdown(f"## 🎯 선택 색상: {selected_color}")
    st.markdown(f"### 💡 심리/성격")
    st.write(info['desc'])
    st.markdown(f"### 🎨 디자인 취향")
    st.write(info['design'])
    st.markdown(f"### 📚 학습 스타일")
    st.write(info['learning'])
    st.markdown(f"### 💼 직업 적합성")
    st.write(info['career'])
