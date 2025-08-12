"""
mbti_career_image.py

설치:
    pip install streamlit pillow

실행:
    streamlit run mbti_career_image.py
"""

import streamlit as st
from io import BytesIO
import csv
import pandas as pd

st.set_page_config(page_title="MBTI 진로 추천 (이미지 버전)", page_icon="💼", layout="centered")

# -----------------------
# 데이터: MBTI 색상, 직업 목록, 기본 이미지(온라인)
# -----------------------
mbti_colors = {
    "ISTJ": "#4A90E2", "ISFJ": "#50E3C2", "INFJ": "#B8E986", "INTJ": "#F5A623",
    "ISTP": "#9013FE", "ISFP": "#F8E71C", "INFP": "#FF8A80", "INTP": "#7B92FF",
    "ESTP": "#00BFA5", "ESFP": "#FF6D00", "ENFP": "#FF4081", "ENTP": "#7C4DFF",
    "ESTJ": "#0091EA", "ESFJ": "#00C853", "ENFJ": "#D500F9", "ENTJ": "#FF1744"
}

# 기본 이미지: Unsplash source (키워드로 이미지를 가져옵니다)
# (인터넷 연결 시 자동으로 관련 이미지가 내려옵니다. 원하면 로컬 업로드도 가능)
mbti_image_queries = {
    "ISTJ": "office,organized",
    "ISFJ": "teacher,helping",
    "INFJ": "counseling,calm",
    "INTJ": "strategy,books",
    "ISTP": "engineer,tools",
    "ISFP": "artist,studio",
    "INFP": "writer,dreamy",
    "INTP": "lab,scientist",
    "ESTP": "entrepreneur,action",
    "ESFP": "stage,performance",
    "ENFP": "creative,ideas",
    "ENTP": "innovation,startup",
    "ESTJ": "manager,office",
    "ESFJ": "care,community",
    "ENFJ": "leadership,people",
    "ENTJ": "business,lead"
}

# 직업 데이터 (아이콘, 제목, 설명)
mbti_jobs = {
    "ISTJ": [
        ("📊", "회계사", "정확성과 꼼꼼함으로 재무를 관리하는 전문가"),
        ("📈", "데이터 분석가", "데이터를 분석해 인사이트를 제공"),
        ("🏛️", "공무원", "공공 서비스와 행정을 담당"),
        ("🛠️", "품질관리자", "제품/서비스 품질을 관리하고 개선")
    ],
    "ISFJ": [
        ("📚", "교사", "학생을 지도하고 교육하는 역할"),
        ("🩺", "간호사", "환자 돌봄과 치료 지원"),
        ("🤝", "사회복지사", "복지서비스로 사람들을 돕는 일"),
        ("📖", "도서관 사서", "자료를 관리하고 이용자를 지원")
    ],
    "INFJ": [
        ("🧠", "상담사", "심리적 지지와 상담을 제공"),
        ("✍️", "작가", "감성적/사유적 글을 창작"),
        ("🔬", "심리학자", "심리 연구와 평가 수행"),
        ("🎨", "예술가", "예술을 통한 메시지 전달")
    ],
    "INTJ": [
        ("🔍", "연구원", "심도있는 연구와 분석 수행"),
        ("📋", "전략기획가", "조직의 중장기 전략을 수립"),
        ("💻", "프로그래머", "소프트웨어 설계 및 개발"),
        ("⚖️", "변호사", "법적 문제 분석 및 해결")
    ],
    "ISTP": [
        ("⚙️", "엔지니어", "실무적 기술 문제 해결"),
        ("🚓", "경찰관", "공공의 안전과 질서를 유지"),
        ("✈️", "항공 정비사", "항공기 점검과 정비"),
        ("📷", "사진작가", "시각적 순간을 포착")
    ],
    "ISFP": [
        ("🎨", "디자이너", "시각적·공간적 아름다움을 창조"),
        ("🎼", "작곡가", "음악을 통한 감정 표현"),
        ("👨‍🍳", "요리사", "맛과 미를 살린 요리 창조"),
        ("🌿", "치유사", "심신의 회복을 돕는 역할")
    ],
    "INFP": [
        ("📖", "소설가", "상상력으로 이야기 창작"),
        ("🧠", "상담가", "정서적 지지 제공"),
        ("🎭", "예술가", "예술을 통한 자기표현"),
        ("🌏", "환경운동가", "환경 보호 활동 주도")
    ],
    "INTP": [
        ("💻", "개발자", "문제를 해결하는 소프트웨어 제작"),
        ("🔬", "과학자", "현상 탐구와 실험 수행"),
        ("💡", "발명가", "새로운 아이디어 구현"),
        ("🎓", "교수", "연구와 교육을 병행")
    ],
    "ESTP": [
        ("🏢", "기업가", "실행력으로 사업을 이끄는 사람"),
        ("💼", "영업사원", "현장에서 성과를 만들어내는 직무"),
        ("🏅", "스포츠 코치", "선수의 기량을 이끌어내는 역할"),
        ("🛫", "파일럿", "항공기 조종 및 운항")
    ],
    "ESFP": [
        ("🎬", "배우", "감정 표현으로 관객과 소통"),
        ("🎉", "이벤트 기획자", "행사를 창의적으로 구성"),
        ("🗺️", "여행 가이드", "현장 경험을 전달하는 역할"),
        ("👗", "스타일리스트", "패션을 통해 이미지 연출")
    ],
    "ENFP": [
        ("📢", "마케터", "브랜드 스토리를 만드는 일"),
        ("🚀", "창업가", "새로운 가치 창출을 시도"),
        ("🎙️", "방송인", "대중과 소통하는 콘텐츠 제작"),
        ("🖌️", "광고 기획자", "광고 콘셉트를 창작")
    ],
    "ENTP": [
        ("💼", "컨설턴트", "문제 해결과 전략 제시"),
        ("🏢", "벤처사업가", "혁신 사업을 운영"),
        ("🏛️", "정치가", "정책과 사회 변화 추진"),
        ("🎬", "프로듀서", "콘텐츠 제작 총괄")
    ],
    "ESTJ": [
        ("📊", "관리자", "조직 운영과 성과 관리"),
        ("🪖", "군인", "국가 안보와 규율 수행"),
        ("📈", "영업 관리자", "영업팀 운용과 목표 관리"),
        ("📋", "프로젝트 매니저", "프로젝트 전반을 컨트롤")
    ],
    "ESFJ": [
        ("🩺", "간호사", "환자 돌봄과 의료 지원"),
        ("📚", "교사", "교육과 인간관계 관리"),
        ("👥", "HR 담당자", "인사와 조직문화를 관리"),
        ("🎉", "이벤트 플래너", "사람 중심의 행사를 기획")
    ],
    "ENFJ": [
        ("🎯", "리더십 코치", "사람의 성장과 팀을 이끄는 역할"),
        ("🎙️", "방송인", "대중과 교감하는 콘텐츠 제작"),
        ("📝", "강사", "지식/기술 전달 전문가"),
        ("🌐", "외교관", "국제 협상과 관계 관리")
    ],
    "ENTJ": [
        ("🏢", "경영자", "조직의 비전과 전략을 이끄는 리더"),
        ("⚖️", "변호사", "법률적 해결과 자문 제공"),
        ("💼", "CEO", "기업 운영과 의사결정"),
        ("📊", "전략 컨설턴트", "경영 문제 해결 전문가")
    ]
}


# -----------------------
# 유틸: Unsplash 이미지 URL 생성 (간단한 기본 이미지)
# -----------------------
def unsplash_url_for(query, w=800, h=500):
    # source.unsplash.com/ (topic) returns a random related image
    # using multiple keywords separated by comma gives varied results
    safe_q = query.replace(" ", ",")
    return f"https://source.unsplash.com/{w}x{h}/?{safe_q}"


# -----------------------
# 사이드바: 설정 (테마, 업로드)
# -----------------------
st.sidebar.header("설정")
st.sidebar.write("원하면 여기에서 이미지 업로드 또는 테마 조절 가능")

# MBTI 기본선택 (사이드바에도 복사)
mbti_list = list(mbti_jobs.keys())
default_mbti = mbti_list[0]
selected_mbti = st.sidebar.selectbox("당신의 MBTI:", mbti_list, index=0)

# 사용자 자체 이미지 업로드 (직업별로 하나씩 업로드해서 카드에 사용 가능)
st.sidebar.markdown("---")
st.sidebar.subheader("이미지 업로드 (선택)")
st.sidebar.write("직업 카드에 표시할 이미지를 업로드하면, 업로드한 이미지가 우선 사용됩니다.")
uploaded_images = {}
for icon, title, desc in mbti_jobs[selected_mbti]:
    key = f"img_{title}"
    uploaded = st.sidebar.file_uploader(f"'{title}' 이미지 업로드", type=["png", "jpg", "jpeg"], key=key)
    if uploaded:
        uploaded_images[title] = uploaded  # BytesIO-like object

# 색상 테마 수동 조정 (선택)
st.sidebar.markdown("---")
if st.sidebar.checkbox("테마 색상 수동 설정", value=False):
    custom_color = st.sidebar.color_picker("테마 색상 선택", value=mbti_colors[selected_mbti])
    mbti_colors[selected_mbti] = custom_color

# -----------------------
# 메인 UI: 헤더
# -----------------------
theme_color = mbti_colors[selected_mbti]
st.markdown(
    f"""
    <style>
    .header {{
        padding: 14px;
        border-radius: 12px;
        background: linear-gradient(90deg, {theme_color}22, {theme_color}11);
        border: 2px solid {theme_color}22;
    }}
    .title {{
        color: {theme_color};
    }}
    .pill {{
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        background:{theme_color}22;
        color:{theme_color};
        font-weight:600;
        border:1px solid {theme_color}33;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(f'<div class="header"><h1 class="title">💼 MBTI 기반 진로 추천 (이미지 카드)</h1>'
            f'<div class="pill">선택: {selected_mbti}</div></div>', unsafe_allow_html=True)

st.write("MBTI를 선택하거나 검색어로 관심 직업을 찾아보세요. 업로드 이미지가 있으면 카드에 표시됩니다.")

# 검색 입력 (메인)
search_term = st.text_input("🔍 직업 키워드로 검색 (예: 디자이너, 변호사, 개발자)")

# 선택 MBTI 강조 영역
st.markdown(f"**테마 색상 미리보기:** <span style='color:{theme_color}; font-weight:700'>{theme_color}</span>", unsafe_allow_html=True)

# -----------------------
# 결과: 카드형 레이아웃 (이미지 포함)
# -----------------------
def render_job_cards(jobs, image_override_map=None):
    # jobs: list of (icon, title, desc)
    cols_per_row = 2  # 컬럼 수 (반응형처럼 보이게)
    for i in range(0, len(jobs), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, job in zip(cols, jobs[i:i+cols_per_row]):
            icon, title, desc = job
            with col:
                # 이미지 결정 (업로드 우선, 아니면 Unsplash)
                if image_override_map and title in image_override_map:
                    st.image(image_override_map[title], use_column_width=True, caption=title)
                else:
                    # unsplash 기본 이미지 (related to MBTI query + job title)
                    q = mbti_image_queries.get(selected_mbti, "career")
                    url = unsplash_url_for(f"{q},{title}")
                    st.image(url, use_column_width=True, caption=title)
                # 카드 스타일 (간단)
                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid {theme_color}22;
                        border-radius: 10px;
                        padding: 10px;
                        margin-top:6px;
                        background: linear-gradient(180deg, #fff, #fff);
                    ">
                        <div style="font-size:18px; color:{theme_color}; font-weight:700;">{icon} {title}</div>
                        <div style="color:#444; margin-top:6px;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# 검색 모드: 전체 데이터에서 탐색
results = []
if search_term:
    term = search_term.lower()
    for mbti_key, jobs in mbti_jobs.items():
        for icon, title, desc in jobs:
            if term in title.lower() or term in desc.lower():
                results.append((icon, title, desc, mbti_key))
    if not results:
        st.info("검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
    else:
        st.subheader(f"🔎 검색 결과: '{search_term}' ({len(results)}개)")
        # show cards; no uploads support in search (we could show if user uploaded for selected MBTI)
        jobs_to_render = [(icon, title, desc) for icon, title, desc, mbti_key in results]
        render_job_cards(jobs_to_render, image_override_map=uploaded_images if uploaded_images else None)

else:
    st.subheader(f"✨ {selected_mbti} 추천 직업")
    jobs_to_render = mbti_jobs[selected_mbti]
    render_job_cards(jobs_to_render, image_override_map=uploaded_images if uploaded_images else None)

# -----------------------
# 추가 기능: CSV 다운로드 (추천 리스트 저장)
# -----------------------
def make_csv_bytes(jobs, mbti_label):
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(["MBTI", "직업명", "설명"])
    for icon, title, desc in jobs:
        writer.writerow([mbti_label, title, desc])
    return output.getvalue()

st.markdown("---")
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("추천 목록 CSV로 저장"):
        csv_bytes = make_csv_bytes(mbti_jobs[selected_mbti], selected_mbti)
        st.download_button("다운로드: CSV", csv_bytes, file_name=f"{selected_mbti}_jobs.csv", mime="text/csv")
with col2:
    st.write("원하면 추천 목록을 CSV로 내려받아 기록할 수 있어요. 학교 과제나 진로 포트폴리오에 활용하기 편합니다.")

# -----------------------
# 푸터: 도움말
# -----------------------
st.markdown("---")
st.write(
    """
    **팁**
    - 카드 이미지가 마음에 들지 않으면 사이드바에서 직업별 이미지를 업로드하세요.
    - Unsplash에서 자동으로 이미지를 불러오므로, 인터넷 연결이 필요합니다.
    - 더 풍부한 데이터를 원하면 직업별 세부 설명(진로 경로, 필요 역량, 관련 학과 등)을 추가해 드릴게요.
    """
)
