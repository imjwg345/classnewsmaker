import streamlit as st
import random
from datetime import date
import requests
from weasyprint import HTML

# 📌 템플릿 목록 (외부 URL)
template_sources = [
    "https://raw.githubusercontent.com/juwan-school/templates/main/canva_style_1.html",
    "https://raw.githubusercontent.com/juwan-school/templates/main/newspaper_style.html"
]

# 🎨 템플릿 불러오기 (예외 처리 포함)
try:
    selected_template_url = random.choice(template_sources)
    response = requests.get(selected_template_url)
    response.raise_for_status()
    html_template = response.text
    st.info(f"✅ 템플릿 불러오기 성공: {selected_template_url}")
except Exception as e:
    st.warning("⚠️ 템플릿을 불러오는 데 문제가 발생했어요. 기본 템플릿을 사용합니다.")
    html_template = """
    <html><head><meta charset="utf-8">
    <style>
    body { font-family: 'Arial'; background-color: #f5f5f5; padding: 30px; }
    h1 { color: #333; font-size: 32px; }
    h2 { color: #333; font-size: 24px; margin-top: 30px; }
    ul { line-height: 1.8; }
    </style></head>
    <body>
    <h1>📢 {date} 학급 소식지</h1>
    <h2>📝 오늘의 소식</h2><ul>{news}</ul>
    <h2>📚 시험 범위</h2><ul>{scope}</ul>
    <h2>🗓️ 시험 시간표</h2><ul>{schedule}</ul>
    <h2>📌 공지사항</h2><ul>{notes}</ul>
    </body></html>
    """

# 📅 날짜
today = date.today().strftime('%Y년 %m월 %d일')

# 📌 항목 선택
st.title("📢 학급 소식지 생성기")
options = st.multiselect("소식지에 포함할 항목을 선택하세요", 
                         ["학급 소식", "시험 범위", "시험 시간표", "공지사항"])

# 📝 입력값 저장용 변수
news_list, scope, schedule, note_list = [], {}, {}, {}

# 📝 학급 소식
if "학급 소식" in options:
    with st.expander("📝 학급 소식 입력"):
        news_items = st.text_area("학급 소식을 입력하세요 (줄바꿈으로 구분)")
        news_list = [item.strip() for item in news_items.split("\n") if item.strip()]

# 📚 시험 범위
if "시험 범위" in options:
    with st.expander("📚 시험 범위 입력"):
        subjects = ["국어", "영어", "수학", "사회", "과학", "정보"]
        scope = {subject: st.text_input(f"{subject} 시험 범위", key=f"scope_{subject}") for subject in subjects}

# 🗓️ 시험 시간표
if "시험 시간표" in options:
    with st.expander("🗓️ 시험 시간표 입력"):
        for i in range(1, 4):
            day = st.text_input(f"{i}일차 날짜", key=f"day_{i}")
            sub1 = st.text_input(f"{i}일차 1교시 과목", key=f"sub1_{i}")
            sub2 = st.text_input(f"{i}일차 2교시 과목", key=f"sub2_{i}")
            if day:
                schedule[day] = [sub1, sub2]

# 📌 공지사항
if "공지사항" in options:
    with st.expander("📌 공지사항 입력"):
        notes = st.text_area("공지사항을 입력하세요 (줄바꿈으로 구분)")
        note_list = [note.strip() for note in notes.split("\n") if note.strip()]

# 📄 템플릿에 내용 삽입
def fill_template(template):
    news_html = "".join(f"<li>{item}</li>" for item in news_list)
    scope_html = "".join(f"<li><strong>{subject}</strong>: {content}</li>" 
                         for subject, content in scope.items() if content)
    schedule_html = "".join(f"<li><strong>{day}</strong>: {subs[0]}, {subs[1]}</li>" 
                            for day, subs in schedule.items())
    notes_html = "".join(f"<li>{note}</li>" for note in note_list)

    filled = template.replace("{date}", today)
    filled = filled.replace("{news}", news_html)
    filled = filled.replace("{scope}", scope_html)
    filled = filled.replace("{schedule}", schedule_html)
    filled = filled.replace("{notes}", notes_html)
    return filled

# 💾 PDF 저장 버튼
if st.button("📁 PDF로 저장하기"):
    final_html = fill_template(html_template)
    pdf_file = f"class_news_{date.today().isoformat()}.pdf"

    try:
        HTML(string=final_html).write_pdf(pdf_file)
        st.success(f"✅ PDF 저장 완료: {pdf_file}")
        st.markdown("👉 PDF 파일은 현재 디렉토리에 저장되어 있어요.")
    except Exception as e:
        st.error("❌ PDF 변환 중 오류가 발생했어요.")
        st.code(str(e))
