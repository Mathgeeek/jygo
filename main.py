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

# CSV 파일 로드 (파일명: restaurants.csv)
try:
    df = pd.read_csv("restaurants.csv") # <-- 파일 이름 변경 적용

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
    st.error("CSV 파일을 찾을 수 없습니다. 파일 이름이 'restaurants.csv'가 맞는지 확인해주세요.") # <-- 파일 이름 변경 적용
    st.stop()
except Exception as e:
    st.error(f"CSV 파일을 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 사이드바 필터링 ---
st.sidebar.header("필터링 옵션")

# 음식 종류 필터
# '음식종류' 컬럼이 없는 경우를 대비하여 get() 메서드 사용 또는 오류 처리 추가
if '음식종류' in df.columns:
    food_types = ['전체'] + sorted(df['음식종류'].dropna().unique().tolist())
    selected_food_type = st.sidebar.selectbox("음식 종류", food_types)
else:
    food_types = ['전체']
    selected_food_type = '전체'
    st.sidebar.warning("CSV 파일에 '음식종류' 컬럼이 없습니다.")


# 주차 난이도 필터
if '주차난이도' in df.columns:
    parking_difficulties = ['전체'] + sorted(df['주차난이도'].dropna().unique().tolist())
    selected_parking_difficulty = st.sidebar.selectbox("주차 난이도", parking_difficulties)
else:
    parking_difficulties = ['전체']
    selected_parking_difficulty = '전체'
    st.sidebar.warning("CSV 파일에 '주차난이도' 컬럼이 없습니다.")


# 데이터 필터링
filtered_df = df.copy()
if selected_food_type != '전체' and '음식종류' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['음식종류'] == selected_food_type]
if selected_parking_difficulty != '전체' and '주차난이도' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['주차난이도'] == selected_parking_difficulty]


st.subheader("📍 지도에서 식당 위치 확인")

# 지도 중심 좌표 설정 (주엽고등학교 근처)
# 주엽고등학교 (대략적인 위도, 경도)
juyeop_school_lat = 445830
juyeop_school_lon = 1160203

# 지도 생성
if filtered_df.empty:
    m = folium.Map(location=[juyeop_school_lat, juyeop_school_lon], zoom_start=15)
    st.warning("선택하신 조건에 맞는 식당이 없습니다. 필터를 조정해주세요.")
else:
    # 필터링된 식당들의 위도/경도 범위를 계산하여 지도 경계 설정
    min_lat, max_lat = filtered_df['위도'].min(), filtered_df['위도'].max()
    min_lon, max_lon = filtered_df['경도'].min(), filtered_df['경도'].max()

    # 지도를 초기화할 때, 필터링된 식당들의 평균 위치를 중심으로 설정
    m = folium.Map(location=[filtered_df['위도'].mean(), filtered_df['경도'].mean()], zoom_start=13)

    # 모든 마커를 포함하는 경계에 지도를 맞춤 (자동 줌 조절)
    # fit_bounds는 [[south_lat, west_lon], [north_lat, east_lon]] 형식의 리스트를 받습니다.
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])


    # 각 식당 위치에 마커 추가
    for idx, row in filtered_df.iterrows():
        # 팝업 정보에 각 컬럼이 있는지 확인하고 있으면 추가
        popup_html = f"<h4>{row['이름']}</h4>"
        if '주소' in row: popup_html += f"<p><strong>주소:</strong> {row['주소']}</p>"
        if '연락처' in row: popup_html += f"<p><strong>연락처:</strong> {row['연락처']}</p>"
        if '음식종류' in row: popup_html += f"<p><strong>음식 종류:</strong> {row['음식종류']}</p>"
        if '주차난이도' in row: popup_html += f"<p><strong>주차 난이도:</strong> {row['주차난이도']}</p>"
        if '휴무' in row: popup_html += f"<p><strong>휴무:</strong> {row['휴무']}</p>"
        if '오픈시간' in row: popup_html += f"<p><strong>오픈 시간:</strong> {row['오픈시간']}</p>"
        if '비고' in row: popup_html += f"<p><strong>비고:</strong> {row['비고']}</p>"

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
    # CSV 파일에 없는 컬럼을 표시하려고 하면 오류가 발생하므로,
    # 실제 df에 있는 열만 선택하도록 로직 강화
    display_columns = ['이름', '주소', '연락처', '음식종류', '주차난이도', '휴무', '오픈시간', '비고']
    final_display_columns = [col for col in display_columns if col in filtered_df.columns]
    st.dataframe(filtered_df[final_display_columns], use_container_width=True)

st.markdown("---")
st.info("이 앱은 주엽고등학교 선생님들을 위한 회식 장소 추천 서비스입니다. 정보 오류가 있을 수 있습니다.")
st.markdown("Made with ❤️ by 선생님")
