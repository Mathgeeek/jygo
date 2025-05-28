import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import math

# 주엽고등학교 위도, 경도
JUYEOP_SCHOOL_LAT = 37.675760 # 선생님이 제공해주신 주엽고 좌표
JUYEOP_SCHOOL_LON = 126.754785 # 선생님이 제공해주신 주엽고 좌표

# --- 거리 계산 함수 (하버사인 공식) ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371 # 지구 반지름 (킬로미터)
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance # 킬로미터 단위

# --- CSV 파일 로드 (웹 게시된 구글 시트 URL 붙여넣기) ---
# 이 URL은 웹에 게시된 CSV 내보내기 URL이어야 합니다.
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR6q6NZYeuslBgpRhgLnjpKOibv56VFnpsBvQDbHvfxE9KnQSUkrVIAF6bCOkrd92EO1JdGrm--H5KW/pub?output=csv"
# 구글 시트의 원본 (편집) 링크. 이건 데이터를 읽어오는 용도가 아님.
GOOGLE_SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1YxB2y-Vvfyk3AKPR8zCYZgldDnAdk_aeaLqbl25Ye34/edit?gid=0#gid=0"

@st.cache_data(ttl=86400) # 24시간마다 데이터 갱신
def load_data(url):
    try:
        df = pd.read_csv(url)
        
        required_columns = ['이름', '주소', '위도', '경도']
        if not all(col in df.columns for col in required_columns):
            st.error(f"구글 시트 CSV 파일에 다음 필수 열 중 하나 이상이 없습니다: {', '.join(required_columns)}")
            st.stop()

        df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
        df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
        df.dropna(subset=['위도', '경도'], inplace=True)
        
        # 각 식당과 학교 간의 거리 계산 및 컬럼 추가
        df['거리(km)'] = df.apply(
            lambda row: haversine_distance(JUYEOP_SCHOOL_LAT, JUYEOP_SCHOOL_LON, row['위도'], row['경도']),
            axis=1
        )
        return df

    except Exception as e:
        st.error(f"구글 시트에서 데이터를 로드하거나 처리하는 중 오류가 발생했습니다: {e}")
        st.stop() # 여기서 stop하면 해당 페이지 로드 자체가 멈춥니다.
        return pd.DataFrame() # 빈 데이터프레임 반환하여 오류 방지

df = load_data(GOOGLE_SHEET_CSV_URL)

# df가 비어있는 경우 (로드 실패 또는 유효 데이터 없음) 페이지에서 메시지 표시
if df.empty:
    st.info("현재 표시할 식당 데이터가 없습니다. 구글 시트를 확인해주세요.")
    # st.stop()는 앱 전체를 멈추므로, 여기서는 단순히 메시지만 표시하고 지도는 그리지 않도록 합니다.
else: # 데이터가 있을 경우에만 지도를 그립니다.
    # --- 메인 페이지 필터링 및 지도 표시 ---

    # 필터링 및 정렬을 위한 공간 분할 (두 개의 컬럼)
    col1, col2 = st.columns([2, 1]) # 지도(2)와 필터/정렬(1)의 비율

    with col2: # 필터링 및 정렬 옵션을 오른쪽에 배치
        # --- 사이드바 상단에 추가할 내용 ---
        st.markdown("## 데이터 정보")
        st.write("이 앱의 데이터는 매 24시간마다 자동으로 업데이트됩니다.")
        # 구글 시트 원본 (편집) 링크를 직접 문자열로 삽입
        st.write(f"[구글 시트 원본 바로 가기]({GOOGLE_SHEET_EDIT_URL})")  # 수정된 부분

        st.markdown("---")  # 구분선
        # --- 기존 필터링 및 정렬 코드 ---
        st.header("필터링 및 정렬")

        # 음식 종류 필터
        if '음식종류' in df.columns:
            food_types = ['전체'] + sorted(df['음식종류'].dropna().unique().tolist())
            selected_food_type = st.selectbox("음식 종류", food_types)
        else:
            food_types = ['전체']
            selected_food_type = '전체'
            st.warning("CSV 파일에 '음식종류' 컬럼이 없습니다.")

        # 주차 난이도 필터
        if '주차난이도' in df.columns:
            parking_difficulties = ['전체'] + sorted(df['주차난이도'].dropna().unique().tolist())
            selected_parking_difficulty = st.selectbox("주차 난이도", parking_difficulties)
        else:
            parking_difficulties = ['전체']
            selected_parking_difficulty = '전체'
            st.warning("CSV 파일에 '주차난이도' 컬럼이 없습니다.")
        
        st.markdown("---") # 구분선
        
        # 정렬 옵션
        sort_options = {
            "이름순 (오름차순)": ("이름", False),
            "이름순 (내림차순)": ("이름", True),
            "거리순 (가까운 순)": ("거리(km)", False),
            "거리순 (먼 순)": ("거리(km)", True)
        }
        selected_sort_option = st.selectbox("정렬 기준", list(sort_options.keys()))

    # 데이터 필터링
    filtered_df = df.copy()
    if selected_food_type != '전체' and '음식종류' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['음식종류'] == selected_food_type]
    if selected_parking_difficulty != '전체' and '주차난이도' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['주차난이도'] == selected_parking_difficulty]

    # 데이터 정렬
    sort_column, ascending = sort_options[selected_sort_option]
    if sort_column in filtered_df.columns: # 정렬 기준 컬럼이 있는지 확인
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)
    else:
        st.warning(f"정렬 기준 '{sort_column}' 컬럼을 찾을 수 없어 정렬되지 않았습니다.")


    with col1: # 지도를 왼쪽에 배치
        st.subheader("📍 지도에서 식당 위치 확인")

        # 지도 생성
        if filtered_df.empty or filtered_df[['위도', '경도']].isnull().all().any():
            m = folium.Map(location=[JUYEOP_SCHOOL_LAT, JUYEOP_SCHOOL_LON], zoom_start=15)
            if filtered_df.empty:
                st.warning("선택하신 조건에 맞는 식당이 없습니다. 필터를 조정해주세요.")
            else:
                st.warning("선택하신 조건에 맞는 식당은 있으나, 유효한 위치 정보가 없어 지도에 표시할 수 없습니다.")
        else:
            min_lat, max_lat = filtered_df['위도'].min(), filtered_df['위도'].max()
            min_lon, max_lon = filtered_df['경도'].min(), filtered_df['경도'].max()

            m = folium.Map(location=[filtered_df['위도'].mean(), filtered_df['경도'].mean()], zoom_start=13)
            m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

            # 주엽고등학교 마커 추가
            folium.Marker(
                location=[JUYEOP_SCHOOL_LAT, JUYEOP_SCHOOL_LON],
                popup=folium.Popup("<strong>주엽고등학교</strong>", max_width=150),
                tooltip="주엽고등학교",
                icon=folium.Icon(color='red', icon='info-sign') # 학교 마커는 빨간색으로 구분
            ).add_to(m)

            # 각 식당 위치에 마커 추가
            for idx, row in filtered_df.iterrows():
                # 위도와 경도 값이 유효한 경우에만 마커 추가
                if pd.notnull(row['위도']) and pd.notnull(row['경도']):
                    popup_html = f"<h4>{row['이름']}</h4>"
                    popup_html += f"<p><strong>주소:</strong> {row.get('주소', '정보 없음')}</p>"
                    popup_html += f"<p><strong>연락처:</strong> {row.get('연락처', '정보 없음')}</p>"
                    popup_html += f"<p><strong>음식 종류:</strong> {row.get('음식종류', '정보 없음')}</p>"
                    popup_html += f"<p><strong>주차 난이도:</strong> {row.get('주차난이도', '정보 없음')}</p>"
                    popup_html += f"<p><strong>휴무:</strong> {row.get('휴무', '정보 없음')}</p>"
                    popup_html += f"<p><strong>오픈 시간:</strong> {row.get('오픈시간', '정보 없음')}</p>"
                    # '거리(km)' 컬럼이 있는지 확인하고 추가 (오류 방지)
                    if '거리(km)' in row:
                        popup_html += f"<p><strong>거리:</strong> {row['거리(km)']:.2f} km</p>" # .2f 포맷팅으로 이미 문자열처럼 처리
                    popup_html += f"<p><strong>비고:</strong> {row.get('비고', '정보 없음')}</p>"

                    folium.Marker(
                        location=[row['위도'], row['경도']],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=row['이름']
                    ).add_to(m)

        folium_static(m, width=800, height=500) # 지도의 너비/높이 조정 가능

    st.subheader("📚 식당 목록")
    if filtered_df.empty:
        st.info("필터링 조건에 맞는 식당이 없습니다.")
    else:
        # 필요한 열만 선택하여 표시 (사용자 편의성 증대)
        # '거리(km)' 컬럼을 표시 목록에 추가
        display_columns = ['이름', '거리(km)', '주소', '연락처', '음식종류', '주차난이도', '휴무', '오픈시간', '비고']
        final_display_columns = [col for col in display_columns if col in filtered_df.columns]
        # '거리(km)' 컬럼이 있을 때만 반올림 적용
        if '거리(km)' in filtered_df.columns:
            st.dataframe(filtered_df[final_display_columns].round({'거리(km)': 2}), use_container_width=True)
        else:
            st.dataframe(filtered_df[final_display_columns], use_container_width=True)

    st.markdown("---")
    st.info("이 앱은 주엽고등학교 선생님들을 위한 회식 장소 추천 서비스입니다. 정보 오류가 있을 수 있습니다.")
    st.markdown("Made with ❤️ by 선생님")
