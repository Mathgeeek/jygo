import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 페이지 설정
st.set_page_config(
    page_title="주엽고 근처 회식 장소 추천",
    page_icon="🏫",
    layout="wide"
)

st.title("🏫 주엽고 근처 회식 장소 추천 웹 앱")
st.write("주엽고등학교 근처의 맛집 정보를 한눈에 확인하고, 지도에서 위치를 찾아보세요!")

# CSV 파일 로드 (깃허브에 업로드한 파일 이름을 정확히 맞춰주세요)
# 파일명에 공백이나 특수문자가 있다면 오류가 발생할 수 있으므로,
# 만약 '주엽고 근처 맛집 List 👍👍 - 시트1.csv' 대신 'restaurants.csv' 등으로 이름을 바꾸시는 것을 추천합니다.
# 저는 이 예제에서는 '주엽고 근처 맛집 List 👍👍 - 시트1.csv'로 가정하겠습니다.
try:
    df = pd.read_csv("restaurants.csv")

    # 필수 컬럼 존재 여부 확인
    required_columns = ['이름', '주소', '위도', '경도']
    if not all(col in df.columns for col in required_columns):
        st.error(f"CSV 파일에 다음 필수 열 중 하나 이상이 없습니다: {', '.join(required_columns)}")
        st.stop()

    # 위도와 경도 데이터 타입 확인 및 변환
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce')

    # 위도/경도 값이 유효하지 않은(NaN) 행 제거
    df.dropna(subset=['위도', '경도'], inplace=True)

    if df.empty:
        st.warning("유효한 위도/경도 데이터가 있는 식당이 없습니다. CSV 파일을 확인해주세요.")
        st.stop()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. 파일 이름이 'restaurants.csv'가 맞는지 확인해주세요.")
    st.stop()
except Exception as e:
    st.error(f"CSV 파일을 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 사이드바 필터링 ---
st.sidebar.header("필터링 옵션")

# 음식 종류 필터
food_types = ['전체'] + sorted(df['음식종류'].dropna().unique().tolist())
selected_food_type = st.sidebar.selectbox("음식 종류", food_types)

# 주차 난이도 필터
parking_difficulties = ['전체'] + sorted(df['주차난이도'].dropna().unique().tolist())
selected_parking_difficulty = st.sidebar.selectbox("주차 난이도", parking_difficulties)

# 데이터 필터링
filtered_df = df.copy()
if selected_food_type != '전체':
    filtered_df = filtered_df[filtered_df['음식종류'] == selected_food_type]
if selected_parking_difficulty != '전체':
    filtered_df = filtered_df[filtered_df['주차난이도'] == selected_parking_difficulty]

st.subheader("📍 지도에서 식당 위치 확인")

# 지도 중심 좌표 설정 (주엽고등학교 근처)
# 주엽고등학교 (대략적인 위도, 경도)
juyeop_school_lat = 37.669818
juyeop_school_lon = 126.764516

# 필터링된 데이터가 없으면 기본 지도를 표시
if filtered_df.empty:
    st.warning("선택하신 조건에 맞는 식당이 없습니다. 필터를 조정해주세요.")
    # 필터링된 데이터가 없어도 지도는 보여줌 (중심은 주엽고)
    m = folium.Map(location=[juyeop_school_lat, juyeop_school_lon], zoom_start=15)
else:
    # 필터링된 식당들의 평균 위치를 지도의 중심으로 설정
    avg_lat = filtered_df['위도'].mean()
    avg_lon = filtered_df['경도'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)

    # 각 식당 위치에 마커 추가
    for idx, row in filtered_df.iterrows():
        popup_html = f"""
        <h4>{row['이름']}</h4>
        <p><strong>주소:</strong> {row['주소']}</p>
        <p><strong>연락처:</strong> {row.get('연락처', '정보 없음')}</p>
        <p><strong>음식 종류:</strong> {row.get('음식종류', '정보 없음')}</p>
        <p><strong>주차 난이도:</strong> {row.get('주차난이도', '정보 없음')}</p>
        <p><strong>휴무:</strong> {row.get('휴무', '정보 없음')}</p>
        <p><strong>오픈 시간:</strong> {row.get('오픈시간', '정보 없음')}</p>
        <p><strong>비고:</strong> {row.get('비고', '정보 없음')}</p>
        """
        folium.Marker(
            location=[row['위도'], row['경도']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['이름']
        ).add_to(m)

# 지도를 스트림릿에 표시
folium_static(m, width=800, height=500)

st.subheader("📚 식당 목록")
if filtered_df.empty:
    st.info("필터링 조건에 맞는 식당이 없습니다.")
else:
    # 필요한 열만 선택하여 표시 (사용자 편의성 증대)
    display_columns = ['이름', '주소', '연락처', '음식종류', '주차난이도', '휴무', '오픈시간', '비고']
    # 실제 df에 있는 열만 선택
    display_columns = [col for col in display_columns if col in filtered_df.columns]
    st.dataframe(filtered_df[display_columns], use_container_width=True)

st.markdown("---")
st.info("이 앱은 주엽고등학교 선생님들을 위한 회식 장소 추천 서비스입니다. 정보 오류가 있을 수 있습니다.")
st.markdown("Made with ❤️ by 선생님")
