import streamlit as st
import pandas as pd

# 구글시트 csv URL
gsheet_url = "https://docs.google.com/spreadsheets/d/1YxB2y-Vvfyk3AKPR8zCYZgldDnAdk_aeaLqbl25Ye34/export?format=csv"

# 데이터 불러오기
df = pd.read_csv(gsheet_url)
df.columns = df.columns.str.strip()  # 혹시 모를 공백 제거

# 컬럼명 확인 (디버깅용, 최초에만 사용)
# st.write(df.columns.tolist())

st.title("우리 학교 근처 회식장소 모음")

# 사이드바 필터
with st.sidebar:
    st.header("필터")
    food_types = st.multiselect('음식종류', sorted(df['음식종류'].dropna().unique()))
    parking = st.multiselect('주차난이도', sorted(df['주차난이도'].dropna().unique()))
    holiday = st.multiselect('휴무', sorted(df['휴무'].dropna().unique()))

# 필터링 적용
filtered = df.copy()
if food_types:
    filtered = filtered[filtered['음식종류'].isin(food_types)]
if parking:
    filtered = filtered[filtered['주차난이도'].isin(parking)]
if holiday:
    filtered = filtered[filtered['휴무'].isin(holiday)]

st.subheader("회식장소 리스트")
st.dataframe(filtered, use_container_width=True)

# 상세 정보 출력
for idx, row in filtered.iterrows():
    st.markdown(f"---\n### {row['이름']}")
    st.write(f"**주소:** {row['주소']}")
    st.write(f"**연락처:** {row['연락처']}")
    st.write(f"**음식종류:** {row['음식종류']}")
    st.write(f"**주차난이도:** {row['주차난이도']}")
    st.write(f"**휴무:** {row['휴무']}  |  **오픈시간:** {row['오픈시간']}")

