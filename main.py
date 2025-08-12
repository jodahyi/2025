# mbti_career_pro.py
"""
MBTI Career Pro (Single-file Streamlit app)
Features:
- 16 MBTI types with 4 curated job suggestions and descriptions each
- MBTI-based color themes (auto-applied)
- Beautiful UI: Google Fonts, responsive grid, hover effects, gradient header
- Search & filter across all jobs
- Image: user-uploaded image overrides or Unsplash fallback
- Favorites (session_state), CSV download, shareable result link (simple)
- Job detail expanders with recommended majors/skills/steps
"""

import streamlit as st
from io import BytesIO
import csv
import pandas as pd
from PIL import Image
import textwrap

st.set_page_config(page_title="MBTI Career Pro", page_icon="🎯", layout="wide")

# -----------------------
# Utilities
# -----------------------
def unsplash_url(q, w=1200, h=800):
    q_safe = q.replace(" ", ",")
    return f"https://source.unsplash.com/{w}x{h}/?{q_safe}"

def csv_bytes_from_jobs(jobs, mbti_label=None):
    out = BytesIO()
    writer = csv.writer(out)
    writer.writerow(["MBTI", "Job Title", "Short Description", "Icon", "Recommended Majors", "Key Skills"])
    for job in jobs:
        icon = job.get("icon","")
        title = job["title"]
        desc = job["desc"]
        majors = "; ".join(job.get("majors", []))
        skills = "; ".join(job.get("skills", []))
        writer.writerow([mbti_label or job.get("mbti",""), title, desc, icon, majors, skills])
    return out.getvalue()

def make_share_url(mbti, job_title):
    # simple share link placeholder (would be replaced by real domain in production)
    base = "https://example.com/career"
    return f"{base}?mbti={mbti}&job={st.experimental_get_query_params().get('job',[job_title])[0]}"

# -----------------------
# Theme / Fonts / CSS
# -----------------------
MBTI_COLORS = {
    "ISTJ": "#2B6CB0", "ISFJ": "#319795", "INFJ": "#805AD5", "INTJ": "#D69E2E",
    "ISTP": "#1A202C", "ISFP": "#ED8936", "INFP": "#D53F8C", "INTP": "#2B6CB0",
    "ESTP": "#DD6B20", "ESFP": "#ED64A6", "ENFP": "#38A169", "ENTP": "#4C51BF",
    "ESTJ": "#2C7A7B", "ESFJ": "#DD6B20", "ENFJ": "#9F7AEA", "ENTJ": "#E53E3E"
}

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700;800&display=swap" rel="stylesheet">
<style>
:root{ --radius:14px; }
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; background: linear-gradient(180deg, #f6f9fc, #ffffff); }

/* Header */
.app-header {
  padding: 28px;
  border-radius: 16px;
  margin-bottom: 20px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 20px;
}
.brand {
  display:flex; align-items:center; gap:16px;
}
.brand .logo {
  width:68px; height:68px; border-radius:12px; display:flex; align-items:center; justify-content:center;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(0,0,0,0.03));
  box-shadow: 0 6px 18px rgba(16,24,40,0.06);
  font-weight:800; font-size:24px;
}
.title {
  font-size:22px; font-weight:800; color:#111827;
}
.subtitle { color:#6B7280; font-size:13px; }

/* Controls */
.controls { display:flex; gap:12px; align-items:center; }

/* Cards grid */
.grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:20px; }
.job-card {
  background: #fff; border-radius: var(--radius); padding:0; overflow:hidden;
  box-shadow: 0 8px 30px rgba(13, 38, 59, 0.06);
  transition: transform .18s ease, box-shadow .18s ease;
}
.job-card:hover { transform: translateY(-6px); box-shadow: 0 14px 40px rgba(13, 38, 59, 0.10); }
.job-media { width:100%; height:180px; object-fit:cover; display:block; }
.job-body { padding:18px; }
.job-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }
.job-title { font-weight:700; font-size:18px; }
.job-icon { font-size:24px; }
.job-desc { margin-top:8px; color:#374151; font-size:14px; line-height:1.35; }
.badge { font-size:12px; padding:6px 10px; border-radius:999px; font-weight:600; }

/* footer */
.footer { margin-top:28px; color:#9CA3AF; font-size:13px; text-align:center; padding:18px; }

@media(max-width:640px){
  .job-media { height:140px; }
  .controls { flex-direction:column; align-items:stretch; gap:10px; }
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# MBTI Data (16 types) - each has list of 4 jobs with details
# For images we use unsplash queries; in production replace with curated assets.
# -----------------------
MBTI_JOBS = {
    "ISTJ": [
        {"title":"회계사", "icon":"📊", "desc":"정확성과 윤리로 재무와 세무를 관리하는 전문가.",
         "majors":["회계학","경영학"], "skills":["엑셀·재무회계","세무지식"], "img_q":"accounting office finance"},
        {"title":"데이터 분석가", "icon":"📈", "desc":"데이터에서 인사이트를 추출해 의사결정을 돕는 역할.",
         "majors":["통계학","컴퓨터공학"], "skills":["SQL","통계분석"], "img_q":"data analytics office"},
        {"title":"공무원", "icon":"🏛️", "desc":"안정적인 조직에서 공공서비스를 제공하는 직무.",
         "majors":["행정학","법학"], "skills":["문서작성","정책이해"], "img_q":"government office building"},
        {"title":"품질관리자", "icon":"🛠️", "desc":"제품·서비스 품질 유지와 개선을 책임지는 전문가.",
         "majors":["산업공학","기계공학"], "skills":["QC","문제해결"], "img_q":"quality control manufacturing"}
    ],
    "ISFJ": [
        {"title":"교사","icon":"📚","desc":"학생을 돌보고 가르치며 성장의 기반을 만드는 직업.",
         "majors":["교육학"], "skills":["수업기획","소통"], "img_q":"teacher classroom"},
        {"title":"간호사","icon":"🩺","desc":"환자 돌봄과 의료지원에서 핵심 역할을 수행.",
         "majors":["간호학"], "skills":["환자관리","응급처치"], "img_q":"nurse hospital care"},
        {"title":"사회복지사","icon":"🤝","desc":"복지서비스로 취약계층의 삶을 지원하는 전문가.",
         "majors":["사회복지학"], "skills":["상담","자원연계"], "img_q":"community social work"},
        {"title":"도서관 사서","icon":"📖","desc":"정보자원의 관리와 이용자 지원을 담당.",
         "majors":["문헌정보학"], "skills":["자료관리","정보검색"], "img_q":"library bookshelves"}
    ],
    "INFJ": [
        {"title":"상담사","icon":"🧠","desc":"개인의 내면을 이해하고 변화를 돕는 심리전문가.",
         "majors":["심리학"], "skills":["경청·상담기술","심리평가"], "img_q":"therapy counseling"},
        {"title":"작가","icon":"✍️","desc":"사유와 감성을 글로 풀어내는 창작자.",
         "majors":["문예창작","국문학"], "skills":["글쓰기","관찰력"], "img_q":"writer desk creative"},
        {"title":"심리학자","icon":"🔬","desc":"심리 연구를 통해 인간 행동을 과학적으로 탐구.",
         "majors":["심리학"], "skills":["연구설계","통계분석"], "img_q":"psychology lab research"},
        {"title":"예술가","icon":"🎨","desc":"감성·메시지를 이미지로 표현하는 창작자.",
         "majors":["미술","디자인"], "skills":["크리에이티브","시각화"], "img_q":"artist studio painting"}
    ],
    "INTJ": [
        {"title":"연구원","icon":"🔍","desc":"전문 분야의 문제를 풀고 지식을 확장하는 역할.",
         "majors":["전공특화"], "skills":["논리적사고","실험설계"], "img_q":"scientist lab research"},
        {"title":"전략기획가","icon":"📋","desc":"조직의 장기 목표와 실행계획을 설계.",
         "majors":["경영학","경제학"], "skills":["전략수립","데이터해석"], "img_q":"strategy planning"},
        {"title":"프로그래머","icon":"💻","desc":"시스템/서비스를 설계·구현하여 문제를 해결.",
         "majors":["컴퓨터공학"], "skills":["코딩","시스템설계"], "img_q":"programmer coding laptop"},
        {"title":"변호사","icon":"⚖️","desc":"법적 문제 해결과 권리 보호를 담당.",
         "majors":["법학"], "skills":["논리·글쓰기","법리해석"], "img_q":"lawyer books courtroom"}
    ],
    "ISTP": [
        {"title":"엔지니어","icon":"⚙️","desc":"현실 문제를 기술적으로 해결하는 실무전문가.",
         "majors":["기계·전기·전자"], "skills":["기술분석","현장해결"], "img_q":"engineer workshop tools"},
        {"title":"경찰관","icon":"🚓","desc":"공공안전과 질서유지를 책임지는 직업.",
         "majors":["경찰행정"], "skills":["신속대응","위기관리"], "img_q":"police patrol"},
        {"title":"항공 정비사","icon":"✈️","desc":"항공기의 안전운항을 위해 정비·점검 수행.",
         "majors":["항공정비"], "skills":["정비기술","세심함"], "img_q":"aircraft maintenance hangar"},
        {"title":"사진작가","icon":"📷","desc":"시각을 통해 순간을 예술화하는 창작자.",
         "majors":["사진예술"], "skills":["구도·디자인","촬영기술"], "img_q":"photographer camera portrait"}
    ],
    "ISFP": [
        {"title":"디자이너","icon":"🎨","desc":"공간·시각을 아름답게 설계하는 창작자.",
         "majors":["디자인"], "skills":["색채·레이아웃","창의력"], "img_q":"designer studio workspace"},
        {"title":"작곡가","icon":"🎼","desc":"음악으로 감정을 구성하고 전달하는 전문가.",
         "majors":["음악"], "skills":["작곡·편곡","음악이론"], "img_q":"composer studio music"},
        {"title":"요리사","icon":"👨‍🍳","desc":"미각과 미감을 결합해 음식을 창조.",
         "majors":["조리학"], "skills":["조리기술","프레젠테이션"], "img_q":"chef kitchen plating"},
        {"title":"치유사","icon":"🌿","desc":"몸과 마음의 회복을 돕는 치료적 역할.",
         "majors":["대체의학"], "skills":["공감·케어","테라피기법"], "img_q":"healing therapy wellness"}
    ],
    "INFP": [
        {"title":"소설가","icon":"📖","desc":"내면의 상상과 메시지를 글로 구현하는 작가.",
         "majors":["문예창작"], "skills":["창의적서사","문장력"], "img_q":"novelist writing desk"},
        {"title":"상담가","icon":"🧠","desc":"정서적 지원과 변화의 촉진을 돕는 역할.",
         "majors":["심리학"], "skills":["경청·공감","상담기법"], "img_q":"counseling session"},
        {"title":"예술가","icon":"🎭","desc":"감정과 아이디어를 예술작업으로 표현.",
         "majors":["미술·연극"], "skills":["표현력","창작"], "img_q":"artist gallery creative"},
        {"title":"환경운동가","icon":"🌏","desc":"지구와 사회를 위한 실천과 캠페인을 이끎.",
         "majors":["환경학"], "skills":["조직화","캠페인기획"], "img_q":"environment activism nature"}
    ],
    "INTP": [
        {"title":"개발자","icon":"💻","desc":"논리적 문제를 코드로 해결하고 제품을 완성.",
         "majors":["컴퓨터공학"], "skills":["알고리즘·코딩","시스템디자인"], "img_q":"developer coding laptop"},
        {"title":"과학자","icon":"🔬","desc":"자연·현상을 분석하고 지식을 확장.",
         "majors":["자연과학"], "skills":["실험·자료해석","논문작성"], "img_q":"science laboratory research"},
        {"title":"발명가","icon":"💡","desc":"새로운 아이디어를 제품·서비스로 구현.",
         "majors":["융합공학"], "skills":["문제발견","프로토타이핑"], "img_q":"invention prototype workshop"},
        {"title":"교수","icon":"🎓","desc":"연구와 교육을 통해 지식을 전파.",
         "majors":["전공심화"], "skills":["연구·강의","논리정리"], "img_q":"university lecture hall"}
    ],
    "ESTP": [
        {"title":"기업가","icon":"🏢","desc":"실행력으로 기회를 포착해 사업을 성장시킴.",
         "majors":["경영학"], "skills":["리스크테이킹","영업"], "img_q":"entrepreneur startup office"},
        {"title":"영업사원","icon":"💼","desc":"현장에서 고객 가치를 만들고 성과를 창출.",
         "majors":["경영·마케팅"], "skills":["소통·협상","영업전략"], "img_q":"sales meeting handshake"},
        {"title":"스포츠 코치","icon":"🏅","desc":"선수의 기량을 끌어올리고 전략을 설계.",
         "majors":["체육"], "skills":["훈련설계","동기부여"], "img_q":"sports coach training"},
        {"title":"파일럿","icon":"🛫","desc":"항공 운항과 승객 안전을 책임지는 전문조종사.",
         "majors":["항공운항"], "skills":["조종술·응급대응","공간지각"], "img_q":"pilot cockpit flying"}
    ],
    "ESFP": [
        {"title":"배우","icon":"🎬","desc":"연기와 표현으로 관객과 감정을 나누는 직업.",
         "majors":["연기·무대"], "skills":["연기·표현","대중소통"], "img_q":"actor stage performance"},
        {"title":"이벤트 기획자","icon":"🎉","desc":"크고 작은 행사를 창의적으로 실행.",
         "majors":["문화기획"], "skills":["프로젝트관리","현장운영"], "img_q":"event planning stage"},
        {"title":"여행 가이드","icon":"🗺️","desc":"현장에서 경험을 전달하고 여행을 완성.",
         "majors":["관광·문화"], "skills":["설명·안내","문제대응"], "img_q":"tour guide travel"},
        {"title":"스타일리스트","icon":"👗","desc":"이미지와 패션을 통해 사람을 연출.",
         "majors":["패션"], "skills":["스타일링","트렌드분석"], "img_q":"stylist fashion studio"}
    ],
    "ENFP": [
        {"title":"마케터","icon":"📢","desc":"창의적 스토리로 브랜드와 고객을 연결.",
         "majors":["마케팅"], "skills":["콘텐츠기획","브랜딩"], "img_q":"marketing creative team"},
        {"title":"창업가","icon":"🚀","desc":"아이디어를 현실로 만들고 조직을 성장.",
         "majors":["경영"], "skills":["기획·리더십","제품개발"], "img_q":"startup team brainstorming"},
        {"title":"방송인","icon":"🎙️","desc":"대중과 소통하며 영향력을 만드는 직업.",
         "majors":["미디어"], "skills":["발화력","콘텐츠제작"], "img_q":"podcast studio broadcast"},
        {"title":"광고 기획자","icon":"🖌️","desc":"광고 캠페인으로 메시지를 창작·전달.",
         "majors":["광고·마케팅"], "skills":["콘셉트구성","카피라이팅"], "img_q":"advertising creative concept"}
    ],
    "ENTP": [
        {"title":"컨설턴트","icon":"💼","desc":"문제의 본질을 찾아 해결책을 제시.",
         "majors":["경영·전공"], "skills":["분석·프레젠테이션","전략"], "img_q":"consulting meeting"},
        {"title":"벤처사업가","icon":"🏢","desc":"혁신적 사업으로 시장을 도전·개척.",
         "majors":["경영"], "skills":["네트워킹","제품시장적합성"], "img_q":"venture startup office"},
        {"title":"정치가","icon":"🏛️","desc":"정책과 공공 이슈를 만들어가는 리더.",
         "majors":["정치외교"], "skills":["협상·연설","정책이해"], "img_q":"politics debate podium"},
        {"title":"프로듀서","icon":"🎬","desc":"콘텐츠의 기획·제작을 총괄하는 역할.",
         "majors":["미디어·예술"], "skills":["프로젝트관리","콘텐츠기획"], "img_q":"producer studio production"}
    ],
    "ESTJ": [
        {"title":"관리자","icon":"📊","desc":"조직운영과 성과관리를 책임지는 리더.",
         "majors":["경영"], "skills":["운영관리","리더십"], "img_q":"office manager meeting"},
        {"title":"군인","icon":"🪖","desc":"안보와 규율을 바탕으로 국가를 수호.",
         "majors":["군사학"], "skills":["규율·체력","팀워크"], "img_q":"soldier uniform training"},
        {"title":"영업 관리자","icon":"📈","desc":"영업팀을 관리하며 목표를 달성.",
         "majors":["경영·마케팅"], "skills":["성과관리","전략적영업"], "img_q":"sales manager office"},
        {"title":"프로젝트 매니저","icon":"📋","desc":"프로젝트 기획·실행·종료를 총괄.",
         "majors":["경영·IT"], "skills":["PM기술","리스크관리"], "img_q":"project manager planning"}
    ],
    "ESFJ": [
        {"title":"간호사","icon":"🩺","desc":"환자 돌봄과 의료지원의 출발점에서 활약.",
         "majors":["간호학"], "skills":["환자케어","팀워크"], "img_q":"nurse caring patient"},
        {"title":"교사","icon":"📚","desc":"학생의 성장을 돕는 교육현장의 핵심.",
         "majors":["교육학"], "skills":["수업설계","소통"], "img_q":"teacher school classroom"},
        {"title":"HR 담당자","icon":"👥","desc":"조직문화와 인재관리를 담당.",
         "majors":["경영·심리"], "skills":["채용·평가","커뮤니케이션"], "img_q":"hr recruitment office"},
        {"title":"이벤트 플래너","icon":"🎉","desc":"사람을 중심으로 행사를 기획·운영.",
         "majors":["문화기획"], "skills":["조직관리","현장운영"], "img_q":"event planner stage"}
    ],
    "ENFJ": [
        {"title":"리더십 코치","icon":"🎯","desc":"팀과 개인의 성장과 협업을 돕는 전문가.",
         "majors":["심리·교육"], "skills":["코칭","조직개발"], "img_q":"leadership coaching"},
        {"title":"방송인","icon":"🎙️","desc":"메시지를 전달하고 공감을 만드는 역할.",
         "majors":["미디어"], "skills":["화술","콘텐츠제작"], "img_q":"broadcaster studio"},
        {"title":"강사","icon":"📝","desc":"주제 전문성을 교육으로 전달하는 직업.",
         "majors":["전공심화"], "skills":["교육설계","전달력"], "img_q":"teacher lecture classroom"},
        {"title":"외교관","icon":"🌐","desc":"국가 간 협상을 통해 관계를 설계.",
         "majors":["국제관계"], "skills":["언어·협상","국제정책"], "img_q":"diplomat meeting"}
    ],
    "ENTJ": [
        {"title":"경영자","icon":"🏢","desc":"조직의 비전과 전술을 결정하는 최고책임자.",
         "majors":["경영"], "skills":["전략수립","리더십"], "img_q":"ceo office meeting"},
        {"title":"변호사","icon":"⚖️","desc":"법률 문제의 해결과 권리 보호를 담당.",
         "majors":["법학"], "skills":["논리·소송","문서작성"], "img_q":"law firm courtroom"},
        {"title":"CEO","icon":"💼","desc":"기업 전체 운영과 성과에 책임을 지는 역할.",
         "majors":["경영"], "skills":["의사결정","조직운영"], "img_q":"business leader office"},
        {"title":"전략 컨설턴트","icon":"📊","desc":"기업의 핵심 문제를 진단하고 해법 제시.",
         "majors":["경영·경제"], "skills":["분석·전략수립","프레젠테이션"], "img_q":"strategy consultant meeting"}
    ]
}

# -----------------------
# Sidebar controls: MBTI select, search, upload images, theme override
# -----------------------
st.sidebar.markdown("## 🔧 설정")
selected_mbti = st.sidebar.selectbox("MBTI 선택", list(MBTI_JOBS.keys()), index=0)

search = st.sidebar.text_input("🔎 키워드 검색 (직업명 · 설명 · 스킬)", "")
only_show_selected = st.sidebar.checkbox("선택 MBTI만 보기", value=True)

st.sidebar.markdown("---")
st.sidebar.write("직업 카드에 사용할 이미지를 업로드하면 해당 직업 카드에서 우선 사용됩니다.")
uploaded_images = {}
# allow uploading images for each job of selected mbti:
for job in MBTI_JOBS[selected_mbti]:
    key = f"upload_{selected_mbti}_{job['title']}"
    uploaded = st.sidebar.file_uploader(f"'{job['title']}' 이미지 업로드", type=["png","jpg","jpeg"], key=key)
    if uploaded:
        uploaded_images[job['title']] = uploaded

st.sidebar.markdown("---")
if st.sidebar.checkbox("테마 색 직접 설정", value=False):
    c = st.sidebar.color_picker("테마 색상 선택", MBTI_COLORS[selected_mbti])
    MBTI_COLORS[selected_mbti] = c

# -----------------------
# Header
# -----------------------
theme = MBTI_COLORS[selected_mbti]
st.markdown(f"""
<div class="app-header" style="background: linear-gradient(90deg, {theme}33, #ffffff); border:1px solid {theme}22;">
  <div class="brand">
    <div class="logo" style="background: linear-gradient(135deg, {theme}, #ffffff33); color:#fff;">MC</div>
    <div>
      <div class="title">MBTI Career Pro</div>
      <div class="subtitle">MBTI 기반 맞춤형 진로 추천 · 탐색 · 저장</div>
    </div>
  </div>
  <div class="controls">
    <div style="display:flex; gap:10px; align-items:center;">
      <div class="badge" style="background:{theme}22; color:{theme}; border:1px solid {theme}33;">선택: {selected_mbti}</div>
      <div class="badge" style="background:#fff; color:#374151; border:1px solid #E5E7EB;">총 유형: 16</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Main controls row
# -----------------------
left, right = st.columns([3,1])
with left:
    q = st.text_input("직업 검색 · 필터 (예: 디자이너, 데이터, 소통)", value=search, placeholder="직업명/설명/스킬로 검색")
with right:
    st.write(" ")
    st.write(" ")
    if st.button("모두 초기화"):
        st.experimental_set_query_params()
        # clear sidebar uploads can't be programmatically cleared; user can replace

# -----------------------
# Build job list to show
# -----------------------
all_cards = []
for mbti_type, jobs in MBTI_JOBS.items():
    for job in jobs:
        item = job.copy()
        item["mbti"] = mbti_type
        # image preference: if user uploaded for selected MBTI, we map after selection for display
        item["img_q"] = job.get("img_q", job["title"])
        all_cards.append(item)

# Apply search & filter
display_cards = []
q_lower = (q or "").strip().lower()
for item in all_cards:
    # filter by MBTI selection if requested
    if only_show_selected and item["mbti"] != selected_mbti:
        continue
    if q_lower:
        hay = " ".join([item["title"], item["desc"], " ".join(item.get("skills", [])), " ".join(item.get("majors", []))]).lower()
        if q_lower in hay:
            display_cards.append(item)
    else:
        display_cards.append(item)

# Sort: show selected MBTI's items first
display_cards.sort(key=lambda x: (0 if x["mbti"]==selected_mbti else 1, x["title"]))

# -----------------------
# Render grid of cards
# -----------------------
st.markdown("### 🔎 결과")
if not display_cards:
    st.info("검색 결과가 없습니다. 키워드를 바꿔보세요.")
else:
    cols_per_row = 3
    # responsive grid via CSS grid; but we will use Streamlit columns loop
    rows = [display_cards[i:i+cols_per_row] for i in range(0, len(display_cards), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row):
            with col:
                # choose image: uploaded (only for selected_mbti) else unsplash fallback
                img_obj = None
                if item["mbti"] == selected_mbti and item["title"] in uploaded_images:
                    img_obj = uploaded_images[item["title"]]
                # Display image
                if img_obj:
                    try:
                        st.image(img_obj, use_column_width=True)
                    except:
                        st.image(Image.open(img_obj), use_column_width=True)
                else:
                    url = unsplash_url(f"{item['img_q']},{item['title']}")
                    st.image(url, use_column_width=True)
                # card body
                st.markdown(f"""
                    <div class="job-body">
                      <div class="job-head">
                        <div>
                          <div class="job-title">{item['icon']} {item['title']}</div>
                          <div style="font-size:12px; color:#6B7280; margin-top:6px;">MBTI: <strong style="color:{MBTI_COLORS[item['mbti']]};">{item['mbti']}</strong></div>
                        </div>
                        <div style="text-align:right;">
                          <div style="font-size:12px; color:#9CA3AF;">추천 전공</div>
                          <div style="font-weight:600; margin-top:6px;">{', '.join(item.get('majors', ['–']))}</div>
                        </div>
                      </div>
                      <div class="job-desc">{item['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)

                # expand for details + action buttons
                key = f"exp_{item['mbti']}_{item['title']}"
                with st.expander("자세히 보기 · 활동/스킬/진로 경로"):
                    st.markdown(f"**권장 전공 / 교육 경로**: {', '.join(item.get('majors', ['관련 전공 다양']))}")
                    st.markdown(f"**핵심 역량(스킬)**: {', '.join(item.get('skills', ['커뮤니케이션 등']))}")
                    steps = [
                        f"1) 관련 기본 과목 수강: {', '.join(item.get('majors', ['기본과목']))}",
                        "2) 실무 경험(인턴/프로젝트) 쌓기",
                        "3) 포트폴리오 및 관련 자격증 준비",
                        "4) 진로 관련 네트워킹 및 멘토링"
                    ]
                    st.markdown("<br>".join(steps), unsafe_allow_html=True)
                    # favorite button
                    fav_key = f"fav_{item['mbti']}_{item['title']}"
                    if st.button("⭐ 즐겨찾기 추가", key=fav_key):
                        if "favorites" not in st.session_state:
                            st.session_state["favorites"] = []
                        entry = {"mbti":item["mbti"], "title":item["title"], "desc":item["desc"]}
                        if entry not in st.session_state["favorites"]:
                            st.session_state["favorites"].append(entry)
                            st.success("즐겨찾기에 추가되었습니다.")
                        else:
                            st.warning("이미 즐겨찾기에 있습니다.")
                    # share + download
                    col1, col2 = st.columns([1,1])
                    with col1:
                        share_link = make_share_url(item["mbti"], item["title"])
                        st.markdown(f"[🔗 공유 링크 생성]({share_link})", unsafe_allow_html=True)
                    with col2:
                        csv_bytes = csv_bytes_from_jobs([item], item["mbti"])
                        st.download_button("📥 이 직업 CSV 저장", csv_bytes, file_name=f"{item['title']}.csv", mime="text/csv")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# -----------------------
# Favorites panel & CSV export for favorites
# -----------------------
st.markdown("---")
st.markdown("### 📌 내 즐겨찾기")
if "favorites" in st.session_state and st.session_state["favorites"]:
    favs = st.session_state["favorites"]
    df = pd.DataFrame(favs)
    st.dataframe(df.rename(columns={"mbti":"MBTI","title":"직업","desc":"설명"}), use_container_width=True)
    csv_all = csv_bytes_from_jobs([{"title":f['title'],"desc":f['desc'],"icon":""} for f in favs], mbti_label="favorite")
    st.download_button("🔽 즐겨찾기 전체 CSV 다운로드", csv_all, file_name="favorites.csv", mime="text/csv")
else:
    st.info("즐겨찾기한 직업이 없습니다. 관심 있는 직업을 찾아 추가해보세요!")

# -----------------------
# Footer
# -----------------------
st.markdown(f"""
<div class="footer">
  MBTI Career Pro · Demo · 디자인/데이터는 샘플입니다. <br>
  이미지: Unsplash (자동 검색) · 프로덕션에서는 자체 자산 사용 권장 · © 2025
</div>
""", unsafe_allow_html=True)

