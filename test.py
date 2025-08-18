import streamlit as st
import pandas as pd
import requests

# ---------------------
# 🎨 앱 기본 설정
# ---------------------
st.set_page_config(page_title="KIA Tigers Fan App", layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #000000;
        color: white;
    }
    .title {
        text-align: center;
        color: #FF0000;
        font-size: 40px;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        color: #FFD700;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------
# 🏆 앱 제목
# ---------------------
st.markdown('<div class="title">⚾ KIA Tigers Fan Hub ⚾</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">KBO 실시간 순위 · 경기일정 · 선수정보</div>', unsafe_allow_html=True)

# ---------------------
# 📊 실시간 순위 (KBO 순위표)
# ---------------------
st.subheader("📊 KBO 팀 순위 (Top 10)")
try:
    url = "https://sports.news.naver.com/kbaseball/record/index?category=kbo"
    tables = pd.read_html(requests.get(url).text)
    ranking_df = tables[0].head(10)
    st.dataframe(ranking_df)
except Exception as e:
    st.error("순위 데이터를 불러올 수 없습니다.")

# ---------------------
# 📅 경기 일정
# ---------------------
st.subheader("📅 KIA Tigers 경기 일정")
try:
    schedule_url = "https://sports.news.naver.com/kbaseball/schedule/index?month=2025-08&category=kbo"
    schedule_tables = pd.read_html(requests.get(schedule_url).text)
    schedule_df = schedule_tables[0]
    st.dataframe(schedule_df)
except Exception:
    st.error("경기 일정을 불러올 수 없습니다.")

# ---------------------
# 🧑‍🤝‍🧑 선수 정보 (샘플)
# ---------------------
st.subheader("🧑‍🤝‍🧑 KIA Tigers 주요 선수 정보")

players = [
    {"name": "최형우", "position": "외야수", "img": "https://imgnews.pstatic.net/image/311/2022/06/15/0001475287_001_20220615162801143.jpg"},
    {"name": "양현종", "position": "투수", "img": "https://imgnews.pstatic.net/image/001/2023/09/08/PYH2023090808740001300_P4_20230908151308086.jpg"},
    {"name": "김도영", "position": "내야수", "img": "https://imgnews.pstatic.net/image/001/2024/04/05/PYH2024040508200001300_P4_20240405150602457.jpg"},
]

cols = st.columns(3)
for i, player in enumerate(players):
    with cols[i]:
        st.image(player["img"], use_container_width=True)
        st.markdown(f"**{player['name']}** - {player['position']}")

# ---------------------
# 🐯 팀 마스코트(호걸이)
# ---------------------
st.subheader("🐯 KIA 타이거즈 마스코트 - 호걸이")
st.image("https://w7.pngwing.com/pngs/449/61/png-transparent-cartoon-tiger-cartoon-tiger-mammal-animals-cartoon.png", width=200)

st.success("KIA Tigers 화이팅! 🔥⚾")
