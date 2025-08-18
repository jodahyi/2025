import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import quote

# =============================
# Page Setup & THEME (KIA colors)
# =============================
st.set_page_config(
    page_title="KIA Tigers Fan App (Live)",
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
    background: linear-gradient(135deg, {PRIMARY_BLACK} 0%, #1f1f1f 50%, {PRIMARY_RED} 100%);
    color: {PRIMARY_WHITE};
  }}
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
    font-size: 24px;
    margin: 8px 0 18px 0;
    font-weight: 700;
  }}
  .subtle {{ color: #dddddd; opacity: 0.9; }}
  .badge {{
    display: inline-block; padding: 2px 8px; border-radius: 999px;
    background: {PRIMARY_RED}; color: {PRIMARY_WHITE}; font-weight: 700; font-size: 12px;
  }}
  .accent {{ color: {PRIMARY_YELLOW}; }}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ===============
# Helper utilities
# ===============
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

@st.cache_data(ttl=900)
def fetch_kbo_standings():
    """Fetch current KBO standings (top 10 teams) from official KBO English site.
    Fallback to MyKBO if needed.
    """
    # Primary: Official KBO (eng)
    url_official = "https://eng.koreabaseball.com/Standings/TeamStandings.aspx"
    try:
        tables = pd.read_html(url_official)
        # Find the table that contains 'RK' or looks like standings
        standings = None
        for t in tables:
            if {'RK','TEAM','W','L','D','PCT'}.issubset(set([str(c).upper() for c in t.columns])):
                standings = t
                break
        if standings is not None:
            # Normalize columns
            cols_map = {c: str(c).strip().upper() for c in standings.columns}
            standings.columns = [cols_map[c] for c in standings.columns]
            standings = standings[["RK","TEAM","W","L","D","PCT"]].head(10)
            standings.columns = ["순위","팀","승","패","무","승률"]
            return standings
    except Exception:
        pass

    # Fallback: MyKBO Stats
    url_mykbo = "https://mykbostats.com/standings"
    try:
        r = requests.get(url_mykbo, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        rows = []
        table = soup.find("table")
        if table:
            for tr in table.find_all("tr")[1:]:
                tds = [td.get_text(strip=True) for td in tr.find_all(["td","th"]) ]
                # Expect format: Rank, Team, W, L, D, PCT, GB, ...
                if len(tds) >= 6 and tds[0].isdigit():
                    rows.append([int(tds[0]), tds[1], tds[2], tds[3], tds[4], tds[5]])
        if rows:
            df = pd.DataFrame(rows, columns=["순위","팀","승","패","무","승률"]).head(10)
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=["순위","팀","승","패","무","승률"])  # empty on failure

@st.cache_data(ttl=900)
def fetch_kia_schedule(days_ahead: int = 21):
    """Fetch KIA Tigers schedule & recent results from MyKBO schedule page.
    Returns many rows, filters to KIA games for the next `days_ahead` days and last 7 days.
    """
    base = "https://mykbostats.com/schedule"
    try:
        r = requests.get(base, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        sections = soup.find_all(["h3","div"])  # dates are often h3
        records = []
        current_date = None
        for el in sections:
            if el.name == "h3":
                # Example: "Friday August 15, 2025"
                txt = el.get_text(" ", strip=True)
                try:
                    current_date = datetime.strptime(txt.split("  ")[0].strip(), "%A %B %d, %Y")
                except Exception:
                    # try a looser parse
                    try:
                        current_date = datetime.strptime(txt.strip(), "%A %B %d, %Y")
                    except Exception:
                        current_date = None
            elif el.name == "div" and current_date:
                # Look for match lines within following siblings
                for item in el.find_all("div"):
                    line = item.get_text(" ", strip=True)
                    if "Kia Tigers" in line or "KIA Tigers" in line or "Kia" in line:
                        records.append({"날짜": current_date.date(), "매치": line})
        df = pd.DataFrame(records)
        if not df.empty:
            today = datetime.today().date()
            mask = (df["날짜"] >= today - timedelta(days=7)) & (df["날짜"] <= today + timedelta(days=days_ahead))
            df = df.loc[mask].sort_values("날짜")
        return df
    except Exception:
        return pd.DataFrame(columns=["날짜","매치"])  # empty

@st.cache_data(ttl=3600)
def fetch_kia_roster_and_stats():
    """Fetch KIA roster & brief stats from MyKBO team page."""
    url = "https://mykbostats.com/teams/5-Kia-Tigers"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # Very simple parse: look for player blocks with name and role
    players = []
    for block in soup.select(".player-card, .player, .col, .row"):
        txt = block.get_text(" ", strip=True)
        # Heuristic: lines with a jersey number and role often contain "+" or "-"
        if len(txt.split()) >= 2 and any(k in txt.lower() for k in ["rp","sp","p","of","if","1b","2b","3b","ss","c"]):
            # Extract name (first two tokens that are likely name-like)
            name = " ".join(txt.split()[:2])
            players.append({"이름": name, "요약": txt})
    df = pd.DataFrame(players).drop_duplicates(subset=["이름"]).head(30)
    return df

@st.cache_data(ttl=3600)
def wikipedia_thumb(person_name: str, size: int = 200) -> str:
    """Try to get a portrait thumbnail URL from Wikipedia for a given player name."""
    try:
        api = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=thumbnail&pithumbsize={size}&titles={quote(person_name)}"
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
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Question_book-new.svg/200px-Question_book-new.svg.png"

# ====================
# Sidebar (Mascot & Theme)
# ====================
st.sidebar.markdown("# 🐯 KIA TIGERS")
st.sidebar.markdown("<span class='badge'>FAN MODE</span>", unsafe_allow_html=True)
mascot_file = st.sidebar.file_uploader("호걸이(마스코트) 이미지 업로드", type=["png","jpg","jpeg","webp"])
mascot_url = st.sidebar.text_input("또는 이미지 URL 입력", "")

if mascot_file is not None:
    st.sidebar.image(mascot_file, caption="호걸이", use_column_width=True)
elif mascot_url:
    st.sidebar.image(mascot_url, caption="호걸이", use_column_width=True)
else:
    st.sidebar.markdown("**Tip:** 호걸이 이미지를 업로드하면 사이드바에 표시됩니다.")

menu = st.sidebar.radio("메뉴", ["오늘의 경기", "경기 일정", "순위표(Top 10)", "선수단"], index=0)

# ====================
# Header
# ====================
st.markdown(f"""
# ⚾ KIA Tigers 팬 앱 <span class='badge'>LIVE</span>
<p class='subtle'>KBO 리그: 실시간 순위/일정/선수 정보 • 테마: <span class='accent'>검정·빨강·노랑·흰색</span></p>
""" , unsafe_allow_html=True)

# ====================
# Pages
# ====================
if menu == "오늘의 경기":
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("### 오늘의 KIA 경기")
        sched = fetch_kia_schedule(days_ahead=7)
        today_str = datetime.today().date()
        today_df = sched[sched["날짜"] == today_str]
        if not today_df.empty:
            for _, r in today_df.iterrows():
                st.markdown(f"<div class='scoreboard'>{r['매치']}</div>", unsafe_allow_html=True)
        else:
            st.info("오늘은 KIA 경기 일정이 없습니다. (최근/다가올 경기들은 아래에서 확인)")
        st.markdown("#### 최근/다가올 경기")
        st.dataframe(sched, use_container_width=True)
    with col2:
        st.markdown("### 현재 순위 (Top 10)")
        st.container(border=True)
        rank = fetch_kbo_standings()
        if not rank.empty:
            st.dataframe(rank, use_container_width=True, height=420)
        else:
            st.warning("순위를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

elif menu == "경기 일정":
    st.markdown("### 📅 KIA 경기 일정 (지난 7일 ~ 다음 3주)")
    df = fetch_kia_schedule(days_ahead=21)
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
        st.table(df.style.highlight_max(axis=0, subset=["승률"]))

elif menu == "선수단":
    st.markdown("### 👥 KIA 타이거즈 선수단 (간략)")
    roster = fetch_kia_roster_and_stats()
    if roster.empty:
        st.warning("선수단 정보를 불러오지 못했습니다. (임시) 이름만 입력하면 위키 사진을 시도해요.")
        default_names = ["Hyoung-woo Choi", "Do-young Kim", "Yang Hyeon-jong", "Gi-yeong Im", "Dae-in Hwang"]
        roster = pd.DataFrame({"이름": default_names, "요약": ["KIA player"]*len(default_names)})
    # Grid display
    n = len(roster)
    cols = st.columns(3)
    for i, (_, row) in enumerate(roster.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{row['이름']}**")
                img = wikipedia_thumb(row['이름'])
                st.image(img, width=160)
                st.caption(row.get("요약", ""))

# ===============
# Footer
# ===============
st.markdown("---")
st.markdown(
    """
    <small>
    데이터 출처: 공식 KBO 영문 사이트, MyKBO Stats, Wikipedia Thumbnails.<br>
    사이트 구조 변경 시 실시간 수집이 실패할 수 있습니다. 문제가 있으면 새로고침하거나 잠시 후 다시 시도해 주세요.
    </small>
    """,
    unsafe_allow_html=True,
)
