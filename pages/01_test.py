import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import math

# 주엽고등학교 위도, 경도
JUYEOP_SCHOOL_LAT = 37.675760
JUYEOP_SCHOOL_LON = 126.754785

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
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/sheets/d/e/2PACX-1vR6q6NZYeuslBgpRhgLnjpKOibv56VFnpsBvQDbHvfxE9KnQSUkrVIAF6bCOkrd92EO1JdGrm--H5KW/pub?output=csv"
GOOGLE_SHEET_EDIT_URL = "https://docs.google.com/sheets/d/1YxB2y-Vvfyk3AKPR8zCYZgldDnAdk_aeaLqbl25Ye34/edit?gid=0#gid=0"

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
        st.stop()
        return pd.DataFrame()

# Streamlit 앱 시작 시 데이터 로드 (캐시 사용)
df = load_data(GOOGLE_SHEET_CSV_URL)

if df.empty:
    st.info("현재 표시할 식당 데이터가 없습니다. 구글 시트를 확인해주세요.")
else:
    # --- CSS 및 메인 페이지 콘텐츠 ---
    st.markdown("""
    <style>
    /* 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Batang&family=Noto+Serif+KR:wght@200..900&family=Orbit&family=Poor+Story&display=swap');
    html, body, [class*="css"] {
        font-family: 'Orbit', sans-serif !important;
    }
    * {
        font-family: 'Orbit', sans-serif !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        transition: none; /* 트랜지션 효과 제거 */
    }
    
    /* 정보 박스 스타일 */
    .info-box {
        background-color: #f0f2f6;
        border-left: 5px solid #4CAF50;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .info-box p {
        margin-bottom: 5px;
        font-size: 0.95rem;
    }
    .stMarkdown a {
        text-decoration: none;
        color: inherit;
    }
    </style>
    """, unsafe_allow_html=True)


    # 필터링 및 정렬을 위한 공간 분할
    col1, col2 = st.columns([2, 1])

    with col2:
        with st.container(border=True):
            st.markdown("""
            <div class="info-box">
                <p>💡 <strong>데이터 업데이트 주기:</strong></p>
                <p>이 앱의 데이터는 매 24시간마다 자동으로 반영됩니다.</p>
                <br>
                <p>데이터 수정이 필요하시면 아래 링크를 통해 원본 시트에 접속해주세요.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.link_button("구글 시트 원본 바로 가기 ➡️", GOOGLE_SHEET_EDIT_URL, help="새 탭에서 구글 시트 원본을 엽니다.")


        st.markdown("---")
        
        with st.container(border=True):
            st.header("나에게 맞는 식당 찾기 ✨")

            # 세션 상태 초기화
            if 'filter_option' not in st.session_state:
                st.session_state.filter_option = 'None'

            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if st.button("주차 걱정 No! 🅿️", help="주차 난이도 '하'인 식당을 우선적으로 보여줍니다.", key="parking_btn"):
                    st.session_state.filter_option = 'parking_easy'
            
            with btn_col2:
                if st.button("학교와의 거리순 🚶‍♀️", help="학교에서 가까운 순서대로 정렬합니다.", key="distance_btn"):
                    st.session_state.filter_option = 'distance_sort'

            if st.button("모든 필터/정렬 해제 🔄", help="모든 필터 및 정렬을 해제하고 초기 상태로 돌아갑니다.", key="reset_btn"):
                st.session_state.filter_option = 'None'

    # ---------------------------------------------------------------
    # 필터링 및 정렬 로직은 이제 `col1` (지도)와 `col2` (필터) 외부에서 독립적으로 처리
    # 이렇게 해야 버튼 클릭 시 로직만 실행되고 지도 재로드를 최소화할 수 있습니다.
    # ---------------------------------------------------------------
    filtered_df = df.copy() # 원본 DataFrame을 복사하여 사용

    if st.session_state.filter_option == 'parking_easy':
        if '주차난이도' in filtered_df.columns:
            filtered_df['parking_temp'] = filtered_df['주차난이도'].astype(str).apply(lambda x: x.split(',')[0].strip() if pd.notnull(x) and isinstance(x, str) else x)
            parking_order = {'하': 0, '중': 1, '상': 2, 'nan': 3, 'None': 3, '':3}
            filtered_df['parking_sort_key'] = filtered_df['parking_temp'].map(parking_order).fillna(3)
            filtered_df = filtered_df.sort_values(by='parking_sort_key', ascending=True).drop(columns='parking_sort_key')
            filtered_df = filtered_df.drop(columns='parking_temp') # 임시 컬럼 삭제
        else:
            st.warning("CSV 파일에 '주차난이도' 컬럼이 없어 주차 필터를 적용할 수 없습니다.")
    elif st.session_state.filter_option == 'distance_sort':
        if '거리(km)' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by='거리(km)', ascending=True)
        else:
            st.warning("CSV 파일에 '거리(km)' 컬럼이 없어 거리순 정렬을 적용할 수 없습니다.")

    # ---------------------------------------------------------------
    # 지도 그리는 부분을 캐싱 함수로 분리
    # 이렇게 하면 버튼 클릭 시 지도 자체는 다시 그려지지 않고,
    # 지도를 구성하는 마커만 변경됩니다.
    # ---------------------------------------------------------------

    @st.cache_resource # 이 데코레이터는 지도를 한번만 생성하여 캐싱합니다.
    def create_base_map(center_lat, center_lon, zoom):
        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)
        # 주엽고등학교 마커는 기본 지도에 포함 (이동하지 않으므로)
        folium.Marker(
            location=[JUYEOP_SCHOOL_LAT, JUYEOP_SCHOOL_LON],
            popup=folium.Popup("<strong>주엽고등학교</strong>", max_width=150),
            tooltip="주엽고등학교",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        return m

    with col1: # 지도를 왼쪽에 배치
        st.subheader("📍 지도에서 식당 위치 확인")

        # 기본 지도 생성 (캐싱됨)
        # filtered_df가 비어있지 않다면 필터링된 식당들의 평균 위치를 사용, 아니면 학교 중심
        map_center_lat = filtered_df['위도'].mean() if not filtered_df.empty else JUYEOP_SCHOOL_LAT
        map_center_lon = filtered_df['경도'].mean() if not filtered_df.empty else JUYEOP_SCHOOL_LON
        
        # 지도를 캐싱된 인스턴스에서 복사하여 마커만 추가/수정
        # 매번 완전히 새로운 지도를 그리지 않고, 캐시된 기본 지도 객체를 수정합니다.
        base_map = create_base_map(map_center_lat, map_center_lon, 13) # 캐시된 기본 지도 가져오기

        # 필터링된 식당이 없거나 유효한 위치 정보가 없으면, 경고 메시지 표시
        if filtered_df.empty or filtered_df[['위도', '경도']].isnull().all().any():
            st.warning("선택하신 조건에 맞는 식당이 없거나, 유효한 위치 정보가 없어 지도에 표시할 수 없습니다.")
            # 빈 지도를 표시
            folium_static(base_map, width=800, height=500)
        else:
            # 지도의 경계를 필터링된 식당들에 맞춤
            min_lat, max_lat = filtered_df['위도'].min(), filtered_df['위도'].max()
            min_lon, max_lon = filtered_df['경도'].min(), filtered_df['경도'].max()
            base_map.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

            # 기존 마커를 제거하고 새 마커 추가 (streamlit-folium 0.6.0 이상에서 동적 마커 업데이트 가능성)
            # 그러나 folium_static은 아직도 전체 지도를 재렌더링하는 경향이 있습니다.
            # 이 부분을 최적화하기 위해선 folium.plugins.MarkerCluster 등을 고려해야 하지만,
            # 현재 코드 구조에서는 지도를 캐싱하는 것이 가장 큰 성능 개선입니다.
            
            # 모든 식당 마커를 base_map에 추가 (기존 마커를 다시 그림)
            for idx, row in filtered_df.iterrows():
                if pd.notnull(row['위도']) and pd.notnull(row['경도']):
                    popup_html = f"<h4>{row['이름']}</h4>"
                    popup_html += f"<p><strong>주소:</strong> {row.get('주소', '정보 없음')}</p>"
                    popup_html += f"<p><strong>연락처:</strong> {row.get('연락처', '정보 없음')}</p>"
                    popup_html += f"<p><strong>음식 종류:</strong> {row.get('음식종류', '정보 없음')}</p>"
                    popup_html += f"<p><strong>주차 난이도:</strong> {row.get('주차난이도', '정보 없음')}</p>"
                    popup_html += f"<p><strong>휴무:</strong> {row.get('휴무', '정보 없음')}</p>"
                    popup_html += f"<p><strong>오픈 시간:</strong> {row.get('오픈시간', '정보 없음')}</p>"
                    if '거리(km)' in row:
                        popup_html += f"<p><strong>거리:</strong> {row['거리(km)']:.2f} km</p>"
                    popup_html += f"<p><strong>비고:</strong> {row.get('비고', '정보 없음')}</p>"

                    folium.Marker(
                        location=[row['위도'], row['경도']],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=row['이름']
                    ).add_to(base_map) # base_map에 마커 추가

            folium_static(base_map, width=800, height=500) # 캐시된 base_map을 표시

    st.subheader("📚 식당 목록")
    if filtered_df.empty:
        st.info("필터링 조건에 맞는 식당이 없습니다.")
    else:
        display_columns = ['이름', '거리(km)', '주소', '연락처', '음식종류', '주차난이도', '휴무', '오픈시간', '비고']
        final_display_columns = [col for col in display_columns if col in filtered_df.columns]
        if '거리(km)' in filtered_df.columns:
            st.dataframe(filtered_df[final_display_columns].round({'거리(km)': 2}), use_container_width=True)
        else:
            st.dataframe(filtered_df[final_display_columns], use_container_width=True)

    st.markdown("---")
    st.info("이 앱은 주엽고등학교 선생님들을 위한 회식 장소 추천 서비스입니다. 정보 오류가 있을 수 있습니다.")
    st.markdown("Made with ❤️ by 선생님")
