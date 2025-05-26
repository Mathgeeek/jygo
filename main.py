import streamlit as st
import pandas as pd

# 구글시트 csv URL 변환
gsheet_url = "https://docs.google.com/spreadsheets/d/1YxB2y-Vvfyk3AKPR8zCYZgldDnAdk_aeaLqbl25Ye34/export?format=csv"

# 데이터 불러오기
df = pd.read_csv(gsheet_url)

# UI 구성
st.title("우리 학교 근처 회식장소 모음")

st.dataframe(df)

# 음식 종류, 가격대, 단체석 등 필터
with st.sidebar:
    st.header("필터")
    food_types = st.multiselect('음식 종류', df['음식종류'].unique())
    price_range = st.multiselect('가격대', df['가격대'].unique())
    group_table = st.selectbox('단체석', ['전체', 'O', 'X'])

filtered = df.copy()
if food_types:
    filtered = filtered[filtered['음식종류'].isin(food_types)]
if price_range:
    filtered = filtered[filtered['가격대'].isin(price_range)]
if group_table != '전체':
    filtered = filtered[filtered['단체석'] == group_table]

st.subheader("회식장소 리스트")
st.dataframe(filtered)

# 지도 표시
if st.checkbox("지도에서 위치 보기"):
    # 위도/경도 결측치 제거
    map_df = filtered.dropna(subset=['위도', '경도'])
    # 위도/경도가 모두 있는 경우에만 표시
    if not map_df.empty:
        st.map(map_df[['위도', '경도']])
    else:
        st.info("위도/경도 정보가 있는 식당만 지도에 표시됩니다.")

# 상세 정보/한줄평
for idx, row in filtered.iterrows():
    st.markdown(f"### {row['이름']}")
    st.write(f"주소: {row['주소']} | 전화: {row['연락처']}")
    st.write(f"음식종류: {row['음식종류']} | 가격대: {row['가격대']} | 단체석: {row['단체석']}")
    st.write(f"한줄평: {row['한줄평']}")
    st.write("---")
