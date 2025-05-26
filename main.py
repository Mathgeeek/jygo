import streamlit as st
import pandas as pd

# 구글시트 csv URL
gsheet_url = "https://docs.google.com/spreadsheets/d/1YxB2y-Vvfyk3AKPR8zCYZgldDnAdk_aeaLqbl25Ye34/export?format=csv"
df = pd.read_csv(gsheet_url)
df.columns = df.columns.str.strip()  # 컬럼명 앞뒤 공백 제거

st.title("우리 학교 근처 회식장소 모음")

# 실제 컬럼명 확인(디버깅용)
st.write("컬럼명:", df.columns.tolist())

# 사이드바 필터 예시 (음식종류, 주차난이도, 영업일)
with st.sidebar:
    st.header("필터")
    food_types = st.multiselect('음식종류', df['음식종류'].dropna().unique())
    parking = st.multiselect('주차난이도', df['주차난이도'].dropna().unique())
    open_days = st.multiselect('영업일', df['영업일'].dropna().unique())

filtered = df.copy()
if food_types:
    filtered = filtered[filtered['음식종류'].isin(food_types)]
if parking:
    filtered = filtered[filtered['주차난이도'].isin(parking)]
if open_days:
    filtered = filtered[filtered['영업일'].isin(open_days)]

st.subheader("회식장소 리스트")
st.dataframe(filtered)

# 상세 정보 표시
for idx, row in filtered.iterrows():
    st.markdown(f"### {row['이름']}")
    st.write(f"주소: {row['주소']} | 전화: {row['연락처']}")
    st.write(f"음식종류: {row['음식종류']} | 주차난이도: {row['주차난이도']} | 영업일: {row['영업일']} | 오픈시간: {row['오픈시간']}")
    st.write("---")
