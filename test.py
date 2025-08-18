import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------------
# 기본 설정 (디자인)
# ----------------------
st.set_page_config(
    page_title="KIA Tigers Fan App",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main {
        background-color: #fff;
        color: #000;
    }
    .stApp header {visibility: hidden;}
    h1, h2, h3, h4, h5, h6 {
        color: #B71C1C; /* 기아 레드 */
    }
    .scoreboard {
        background-color: #000;
        color: #fff;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-size: 24px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# 더미 데이터
# ----------------------

# 경기 일정
schedule = pd.DataFrame({
    "날짜": ["2025-08-18", "2025-08-20", "2025-08-22"],
    "상대": ["두산 베어스", "LG 트윈스", "삼성 라이온즈"],
    "장소": ["광주", "잠실", "대구"]
})

# 순위표
ranking = pd.DataFrame({
    "팀": ["LG", "KIA", "두산", "삼성", "SSG"],
    "승": [65, 62, 58, 55, 52],
    "패": [40, 42, 45, 48, 50],
    "승률": [0.62, 0.60, 0.56, 0.53, 0.51]
})

# 선수 정보
players = pd.DataFrame({
    "선수": ["최형우", "김도영", "양현종"],
    "포지션": ["타자", "내야수", "투수"],
    "주요 기록": ["타율 .312 / HR 15", "도루 25 / 타율 .298", "ERA 3.25 / 8승"]
})

# ----------------------
# UI 구성
# ----------------------

st.title("⚾ KIA Tigers 팬 전용 앱")
st.markdown("KBO 리그 기아 타이거즈의 경기 일정, 선수 정보, 순위를 확인하세요!")

# 사이드바 메뉴
menu = st.sidebar.radio("메뉴 선택", ["오늘의 경기", "경기 일정", "순위표", "선수단"])

# 오늘 경기
if menu == "오늘의 경기":
    st.subheader("📅 오늘의 경기")
    today = datetime.today().strftime("%Y-%m-%d")
    game_today = schedule[schedule["날짜"] == today]

    if not game_today.empty:
        opponent = game_today.iloc[0]["상대"]
        place = game_today.iloc[0]["장소"]
        st.markdown(f"<div class='scoreboard'>KIA 타이거즈 vs {opponent}<br>장소: {place}</div>", unsafe_allow_html=True)
    else:
        st.info("오늘은 경기가 없습니다.")

# 경기 일정
elif menu == "경기 일정":
    st.subheader("📅 경기 일정")
    st.table(schedule)

# 순위표
elif menu == "순위표":
    st.subheader("📊 KBO 순위")
    st.dataframe(ranking, use_container_width=True)

# 선수단
elif menu == "선수단":
    st.subheader("👥 기아 선수단")
    for i, row in players.iterrows():
        st.markdown(f"### {row['선수']} - {row['포지션']}")
        st.write(f"{row['주요 기록']}")
        st.divider()
