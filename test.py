import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

# =============================
# Page Setup & THEME (KIA colors)
# =============================
st.set_page_config(
    page_title="KIA Tigers Fan App (Live, no-bs4)",
    page_icon="🐯",
    layout="wide",
    initial_sidebar_state="expanded"
)

PRIMARY_RED = "#B71C1C"      # KIA Red
PRIMARY_BLACK = "#111111"    # KIA Black (near-black)
PRIMARY_YELLOW = "#FFD54F"   # Soft Yellow accent
PRIMARY_WHITE = "#FFFFFF"

THEME_CSS = f"""
<style>
  .stApp {{
    background: radial-gradient(circle at 20% 20%, {PRIMARY_BLACK} 0%, #1b1b1b 40%, {PRIMARY_RED} 100%);
    color: {PRIMARY_WHITE};
  }}
  h1, h2, h3, h4 {{ color: {PRIMARY_YELLOW}; }}
  .kia-card {{
    background-color: rgba(17,17,17,0.75);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
  }}
  .scoreboard {{
    background: linear-gradient(180deg, #000000, #222222);
    border: 2px solid {PRIMARY_RED};
    color: {PRIMARY_YELLOW};
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    font-size: 22px;
    margin: 8px 0 18px 0;
    font-weight: 700;
  }}
  .badge {{
    display: inline-block; padding: 2px 10px; border-radius: 999px;
    background: {PRIMARY_RED}; color: {PRIMARY_WHITE}; font-weight: 700; font-size: 12px;
  }}
  .accent {{ color: {PRIMARY_YELLOW}; }}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ====================
# Helper utilities (NO bs4)
# ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST)

@st.cache_data(ttl=900)
def fetch_kbo_standings() -> pd.DataFrame:
    """Fetch current KBO standings (top 10) via pandas.read_html (no bs4)."""
    # Primary: KBO ENG
    try:
        url2 = "https://eng.koreabaseball.com/Standings/TeamStandings.aspx"
        html2 = requests.get(url2, headers=HEADERS, timeout=10).text
        tables2 = pd.read_html(html2)
        for t in tables2:
            cols_up = [str(c).upper() for c in t.columns]
            if {"RK","TEAM","W","L","D","PCT"}.issubset(set(cols_up)):
                t.columns = cols_up
                t = t[["RK","TEAM","W","L","D","PCT"]].head(10)
                t.columns = ["순위","팀","승","패","무","승률"]
                return t
    except Exception:
        pass
    # Fallback: Naver
    try:
        url = "https://sports.news.naver.com/kbaseball/record/index?category=kbo"
        html = requests.get(url, headers=HEADERS, timeout=10).text
        tables = pd.read_html(html)
        for df in tables:
            if df.shape[1] >= 6:
                df = df.head(10)
                df.rename(columns={df.columns[0]:"순위"}, inplace=True)
                return df
    except Exception:
        pass
    # Fallback: MyKBO
    try:
        url3 = "https://mykbostats.com/standings"
        html3 = requests.get(url3, headers=HEADERS, timeout=10).text
        tables3 = pd.read_html(html3)
        for df in tables3:
            if df.shape[1] >= 6:
                df = df.head(10)
                df.rename(columns={df.columns[0]:"순위"}, inplace=True)
                return df
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1200)
def fetch_schedule_kia(months_back: int = 1, months_ahead: int = 2) -> pd.DataFrame:
    """Fetch KIA schedule from multiple monthly sources (no bs4)."""
    rows = []
    # 1) Naver monthly schedule
    for m_offset in range(-months_back, months_ahead+1):
        dt = (TODAY.replace(day=1) + timedelta(days=31*m_offset)).replace(day=1)
        month_str = f"{dt.year}-{dt.month:02d}"
        try:
            url = f"https://sports.news.naver.com/kbaseball/schedule/index?month={month_str}&category=kbo"
            html = requests.get(url, headers=HEADERS, timeout=10).text
            tables = pd.read_html(html)
            for t in tables:
                # Normalize all cells to string then filter
                t = t.applymap(lambda x: str(x) if not isinstance(x, str) else x)
                mask = t.apply(lambda r: any("KIA" in c or "기아" in c for c in r), axis=1)
                kia_rows = t[mask]
                if not kia_rows.empty:
                    kia_rows.insert(0, "월", month_str)
                    rows.append(kia_rows)
        except Exception:
            pass
    # 2) STATIZ monthly schedule (fallback)
    if not rows:
        for m_offset in range(-months_back, months_ahead+1):
            dt = (TODAY.replace(day=1) + timedelta(days=31*m_offset)).replace(day=1)
            try:
                url = f"https://www.statiz.co.kr/schedule.php?opt=0&sopt=0&sy={dt.year}&sm={dt.month}"
                html = requests.get(url, headers=HEADERS, timeout=10).text
                tables = pd.read_html(html)
                for t in tables:
                    t = t.applymap(lambda x: str(x) if not isinstance(x, str) else x)
                    mask = t.apply(lambda r: any("KIA" in c or "기아" in c for c in r), axis=1)
                    kia_rows = t[mask]
                    if not kia_rows.empty:
                        kia_rows.insert(0, "월", f"{dt.year}-{dt.month:02d}")
                        rows.append(kia_rows)
            except Exception:
                pass
    if rows:
        out = pd.concat(rows, ignore_index=True)
        out.columns = [str(c) for c in out.columns]
        return out
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def wikipedia_thumb(person_name: str, size: int = 240) -> str:
    """Get a portrait thumbnail URL from Wikipedia for a given player name (no bs4)."""
    try:
        api = (
            "https://en.wikipedia.org/w/api.php?"
            f"action=query&prop=pageimages&format=json&piprop=thumbnail&pithumbsize={size}&titles={quote(person_name)}"
        )
        r = requests.get(api, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for _, p in pages.items():
            thumb = p.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass
    # fallback generic icon
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Question_book-new.svg/240px-Question_book-new.svg.png"

# ====================
# Sidebar (Mascot & Controls)
# ====================
st.sidebar.markdown("# 🐯 KIA TIGERS")
st.sidebar.markdown("<span class='badge'>FAN MODE</span>", unsafe_allow_html=True)
mascot_file = st.sidebar.file_uploader("호걸이(마스코트) 이미지 업로드", type=["png","jpg","jpeg","webp"])
mascot_url = st.sidebar.text_input("또는 이미지 URL 입력", "")
months_back = st.sidebar.slider("지난 개월 수", 0, 3, 1)
months_ahead = st.sidebar.slider("다가올 개월 수", 0, 4, 2)

if mascot_file is not None:
    st.sidebar.image(mascot_file, caption="호걸이", use_column_width=True)
elif mascot_url:
    st.sidebar.image(mascot_url, caption="호걸이", use_column_width=True)
else:
    st.sidebar.caption("Tip: 호걸이 이미지를 업로드하면 사이드바에 표시됩니다.")

menu = st.sidebar.radio("메뉴", ["오늘의 경기", "경기 일정", "순위표(Top 10)", "선수단"], index=0)

# ====================
# Header
# ====================
st.markdown(f"""
# ⚾ KIA Tigers 팬 앱 <span class='badge'>LIVE</span>
<p>테마: <b style='color:{PRIMARY_WHITE}'>검정</b> · <b style='color:{PRIMARY_RED}'>빨강</b> · <b style='color:{PRIMARY_YELLOW}'>노랑</b> · <b style='color:{PRIMARY_WHITE}'>흰색</b></p>
""", unsafe_allow_html=True)

# ====================
# Pages
# ====================
if menu == "오늘의 경기":
    c1, c2 = st.columns([2,1], gap="large")
    with c1:
        st.markdown("### 오늘의 KIA 경기")
        sched = fetch_schedule_kia(months_back=0, months_ahead=0)
        today_strs = [
            TODAY.strftime("%m/%d"),
            TODAY.strftime("%Y-%m-%d"),
            TODAY.strftime("%Y.%m.%d"),
            TODAY.strftime("%m.%d"),
            TODAY.strftime("%-m/%-d") if hasattr(TODAY, 'strftime') else TODAY.strftime("%m/%d"),
        ]
        today_rows = pd.DataFrame()
        if not sched.empty:
            today_rows = sched[sched.apply(lambda r: any(ts in " ".join(map(str, r.values)) for ts in today_strs), axis=1)]
        if not today_rows.empty:
            for _, r in today_rows.iterrows():
                st.markdown(f"<div class='scoreboard'>{' | '.join(map(str, r.values))}</div>", unsafe_allow_html=True)
        else:
            st.info("오늘 경기 정보를 찾지 못했습니다. 아래 '경기 일정' 탭에서 더 많은 일정을 확인하세요.")
    with c2:
        st.markdown("### 현재 순위 (Top 10)")
        rank = fetch_kbo_standings()
        if not rank.empty:
            st.dataframe(rank, use_container_width=True, height=420)
        else:
            st.warning("순위를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

elif menu == "경기 일정":
    st.markdown("### 📅 KIA 경기 일정 (더 많이 보기)")
    df = fetch_schedule_kia(months_back=months_back, months_ahead=months_ahead)
    if df.empty:
        st.warning("일정을 불러오지 못했습니다. 네트워크 또는 원본 사이트 구조 변동일 수 있어요.")
    else:
        st.dataframe(df, use_container_width=True)

elif menu == "순위표(Top 10)":
    st.markdown("### 📊 KBO 순위 (Top 10)")
    df = fetch_kbo_standings()
    if df.empty:
        st.warning("순위를 불러오지 못했습니다.")
    else:
        try:
            st.table(df.style.highlight_max(axis=0, subset=["승률"]))
        except Exception:
            st.dataframe(df, use_container_width=True)

elif menu == "선수단":
    st.markdown("### 👥 KIA 타이거즈 선수단 (사진 자동) ")
    st.caption("선수 이름을 영어로 입력하면 위키 썸네일을 자동으로 불러옵니다. (예: Hyoung-woo Choi, Do-young Kim, Yang Hyeon-jong)")

    default_players = [
        ("Hyoung-woo Choi", "OF"),
        ("Do-young Kim", "IF"),
        ("Yang Hyeon-jong", "P"),
        ("Gi-yeong Im", "P"),
        ("Dae-in Hwang", "IF")
    ]

    names = st.text_area(
        "선수 명단 (쉼표로 구분, 영어)",
        ", ".join([n for n,_ in default_players])
    )
    parsed = [s.strip() for s in names.split(",") if s.strip()]
    if not parsed:
        parsed = [n for n,_ in default_players]

    cols = st.columns(3)
    for i, name in enumerate(parsed):
        img = wikipedia_thumb(name)
        pos = next((p for (n,p) in default_players if n==name), "")
        with cols[i % 3]:
            with st.container(border=True):
                st.image(img, width=200)
                st.markdown(f"**{name}**  {f'· {pos}' if pos else ''}")

# ===============
# Footer
# ===============
st.markdown("---")
st.markdown(
    """
    <small>
    데이터 출처: KBO(ENG), Naver Sports, STATIZ (pandas.read_html 사용).<br>
    페이지 구조 변경 시 일시적으로 로드 실패할 수 있습니다.
    </small>
    """,
    unsafe_allow_html=True,
)
