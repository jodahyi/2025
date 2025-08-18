import streamlit as st

# =====================
# Page Setup & Background
# =====================
st.set_page_config(
    page_title="🎨 색채 심리 테스트",
    page_icon="🖌️",
    layout="wide"
)

# 배경색/그라디언트 적용
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFFAF0, #FFF5EE);
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 나의 색채 심리 테스트")
st.markdown("좋아하는 색을 선택하면 당신의 성격, 디자인 취향, 학습 스타일, 직업 적합성까지 알려줍니다.")

# =====================
# 색상 데이터 (추가 + 상세)
# =====================
color_data = {
    "빨강": {"hex":"#E53935",
        "desc":"열정적이고 용기 있는 성격으로 도전과 경쟁을 즐깁니다. 리더십이 강하고 주변 사람들에게 활력을 줍니다.",
        "design":"강렬한 대비와 포인트 컬러 디자인을 선호합니다.",
        "learning":"실천 위주, 활동적 학습 스타일",
        "career":"리더, 마케터, 운동선수, 활동적인 직업 적합"
    },
    "주황": {"hex":"#FB8C00",
        "desc":"긍정적이고 사교적이며 창의적입니다. 새로운 아이디어를 즐기고 활기차게 움직입니다.",
        "design":"밝고 에너지 넘치는 색상과 패턴을 선호합니다.",
        "learning":"그룹 활동, 아이디어 공유 학습",
        "career":"광고, 기획, 이벤트, 교육 관련 직업 적합"
    },
    "노랑": {"hex":"#FDD835",
        "desc":"낙천적이며 명랑하고 창의력이 풍부합니다. 주변에 활기를 주며 호기심이 많습니다.",
        "design":"밝고 경쾌한 색상, 시각적 강조 디자인 선호",
        "learning":"관찰 및 실험 학습 선호",
        "career":"디자이너, 예술가, 강사 등 창의적 직업 적합"
    },
    "초록": {"hex":"#43A047",
        "desc":"조화롭고 안정적인 성격으로 자연과 균형을 중요시합니다. 차분하며 감정이 안정적입니다.",
        "design":"자연색, 부드럽고 편안한 톤 선호",
        "learning":"계획적 학습, 집중 학습 스타일",
        "career":"환경, 자연, 치유 관련 직업 적합"
    },
    "파랑": {"hex":"#1E88E5",
        "desc":"차분하고 이성적이며 신중합니다. 안정과 신뢰를 중시합니다.",
        "design":"미니멀, 정돈된 레이아웃과 색상 선호",
        "learning":"분석적 학습, 자료 정리 선호",
        "career":"공학, 연구, IT, 관리 직무 적합"
    },
    "보라": {"hex":"#8E24AA",
        "desc":"예술적 감각이 뛰어나고 창의적이며 감성적입니다.",
        "design":"독창적이고 예술적인 패턴 디자인 선호",
        "learning":"상상력, 창의적 프로젝트 중심 학습",
        "career":"예술, 디자인, 창작 관련 직업 적합"
    },
    "분홍": {"hex":"#EC407A",
        "desc":"사교적이고 다정하며 감성적인 성격입니다. 다른 사람에게 관심과 배려를 많이 합니다.",
        "design":"부드럽고 로맨틱한 색상 디자인 선호",
        "learning":"협동 학습, 소통 중심 학습",
        "career":"교육, 상담, 서비스 관련 직업 적합"
    },
    "청록": {"hex":"#00ACC1",
        "desc":"논리적이면서도 차분하며 독창적인 성향이 강합니다.",
        "design":"현대적이고 깔끔한 톤의 디자인 선호",
        "learning":"분석과 관찰 중심 학습 선호",
        "career":"연구, IT, 디자인 직업 적합"
    },
    "갈색": {"hex":"#6D4C41",
        "desc":"현실적이고 신뢰할 수 있는 성격입니다. 안정감과 성실함을 중요시합니다.",
        "design":"내추럴 톤, 편안하고 안정적인 디자인 선호",
        "learning":"체계적, 반복 학습 스타일",
        "career":"관리, 회계, 교육, 자연 관련 직업 적합"
    },
    "검정": {"hex":"#212121",
        "desc":"신비롭고 세련된 이미지를 선호합니다. 집중력과 자기주장이 강합니다.",
        "design":"모던, 심플, 고급스러운 디자인 선호",
        "learning":"집중적 자기주도 학습 선호",
        "career":"디자인, 예술, 기획, 전략적 직무 적합"
    },
    "흰색": {"hex":"#FAFAFA",
        "desc":"순수하고 깔끔하며 평화를 중요시합니다. 객관적이고 새로운 시작을 좋아합니다.",
        "design":"미니멀, 정돈된 디자인 선호",
        "learning":"정리 및 계획 중심 학습 선호",
        "career":"교육, 연구, 기획, 상담 직업 적합"
    },
    "회색": {"hex":"#9E9E9E",
        "desc":"중립적이고 침착하며 분석적인 성격입니다. 감정을 안정적으로 유지합니다.",
        "design":"차분하고 절제된 디자인 선호",
        "learning":"분석적, 논리적 학습 선호",
        "career":"IT, 분석, 회계, 관리 직무 적합"
    }
}

# =====================
# 색상 선택 UI (그리드)
# =====================
st.markdown("### 좋아하는 색을 선택하세요:")
selected_color = st.session_state.get("selected_color", None)

cols = st.columns(4)
for i, (color_name, info) in enumerate(color_data.items()):
    with cols[i % 4]:
        if st.button(color_name):
            selected_color = color_name
            st.session_state["selected_color"] = color_name
        # 버튼 CSS
        st.markdown(f"""
        <style>
        div.stButton > button:contains("{color_name}") {{
            background-color: {info['hex']};
            color: {"#000000" if color_name in ['노랑','청록'] else "#FFFFFF"};
            border-radius: 12px;
            height: 60px;
            font-size: 16px;
            font-weight: bold;
        }}
        </style>
        """, unsafe_allow_html=True)

# =====================
# 결과 출력
# =====================
if selected_color:
    info = color_data[selected_color]
    st.markdown(f"## 🎯 당신이 선택한 색: {selected_color}")
    st.markdown(f"**성격 특징:** {info['desc']}")
    st.markdown(f"**디자인 취향:** {info['design']}")
    st.markdown(f"**학습 스타일:** {info['learning']}")
    st.markdown(f"**직업 적합성:** {info['career']}")
