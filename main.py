import streamlit as st
from PIL import Image
import base64

# ===========================
# 스타일 (CSS) 적용
# ===========================
st.set_page_config(page_title="MBTI Career Finder", page_icon="🎯", layout="wide")

# Google Fonts + Custom CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
            background-color: #f7f9fc;
        }

        .main-title {
            font-size: 48px;
            font-weight: 700;
            text-align: center;
            color: #2d2d2d;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 18px;
            text-align: center;
            color: #555;
            margin-bottom: 50px;
        }

        .job-card {
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.2s ease-in-out;
        }

        .job-card:hover {
            transform: scale(1.02);
            box-shadow: 0px 6px 25px rgba(0,0,0,0.15);
        }

        .job-title {
            font-size: 24px;
            font-weight: 700;
            color: #2e4a7d;
            margin-bottom: 10px;
        }

        .job-desc {
            font-size: 16px;
            color: #333;
            margin-bottom: 20px;
        }

        .footer {
            text-align: center;
            font-size: 14px;
            color: #aaa;
            margin-top: 50px;
        }
    </style>
""", unsafe_allow_html=True)


# ===========================
# 데이터
# ===========================
career_data = {
    "INTJ": {
        "job": "전략 컨설턴트",
        "desc": "복잡한 문제를 체계적으로 분석하고 창의적인 해결책을 제시하는 전문가.",
        "image": "https://images.unsplash.com/photo-1521791136064-7986c2920216"
    },
    "ENFP": {
        "job": "크리에이티브 디렉터",
        "desc": "다양한 아이디어를 시각적으로 표현하고 새로운 트렌드를 이끄는 창의적 리더.",
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d"
    },
    "ISTP": {
        "job": "제품 디자이너",
        "desc": "사용자의 경험을 분석하고 기능과 디자인을 결합한 제품을 만드는 전문가.",
        "image": "https://images.unsplash.com/photo-1581093588401-22d615d3db55"
    },
    "INFJ": {
        "job": "심리상담사",
        "desc": "타인의 감정을 깊이 이해하고 삶의 방향성을 제시하는 공감 전문가.",
        "image": "https://images.unsplash.com/photo-1520975918318-3e8a1f1a0c76"
    },
}

# ===========================
# 헤더
# ===========================
st.markdown("<div class='main-title'>🎯 MBTI Career Finder</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>당신의 MBTI에 맞는 최고의 직업을 찾아드립니다</div>", unsafe_allow_html=True)

# ===========================
# MBTI 선택
# ===========================
col1, col2, col3 = st.columns([1,1,1])
with col2:
    mbti = st.selectbox("당신의 MBTI를 선택하세요", list(career_data.keys()))

# ===========================
# 결과 표시
# ===========================
if mbti:
    job_info = career_data[mbti]
    colA, colB = st.columns([1,1])

    with colA:
        st.markdown(f"<div class='job-card'>"
                    f"<div class='job-title'>{job_info['job']}</div>"
                    f"<div class='job-desc'>{job_info['desc']}</div>"
                    f"</div>", unsafe_allow_html=True)

    with colB:
        st.image(job_info['image'], use_container_width=True)

# ===========================
# 즐겨찾기 기능
# ===========================
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

if st.button("⭐ 즐겨찾기에 추가"):
    if job_info["job"] not in st.session_state["favorites"]:
        st.session_state["favorites"].append(job_info["job"])
        st.success("즐겨찾기에 추가되었습니다!")
    else:
        st.warning("이미 즐겨찾기에 있습니다.")

if st.session_state["favorites"]:
    st.subheader("📌 나의 즐겨찾기")
    for fav in st.session_state["favorites"]:
        st.write(f"- {fav}")

# ===========================
# 공유 기능
# ===========================
share_url = f"https://career.example.com/?mbti={mbti}"
st.markdown(f"[🔗 친구와 공유하기]({share_url})", unsafe_allow_html=True)

# ===========================
# Footer
# ===========================
st.markdown("<div class='footer'>© 2025 MBTI Career Finder. All rights reserved.</div>", unsafe_allow_html=True)

