import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import math

# 페이지 설정
st.set_page_config(
    page_title="주엽고❤️❤️",
    page_icon="🏫",
    layout="wide"
)

# 폰트 설정
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Batang&family=Noto+Serif+KR:wght@200..900&family=Orbit&family=Poor+Story&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Orbit', sans-serif !important;
    }
    * {
        font-family: 'Orbit', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR6q6NZYeuslBgpRhgLnjpKOibv56VFnpsBvQDbHvfxE9KnQSUkrVIAF6bCOkrd92EO1JdGrm--H5KW/pub?output=csv"
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
        st.stop()
        return pd.DataFrame()

df = load_data(GOOGLE_SHEET_CSV_URL)

if df.empty:
    st.info("현재 표시할 식당 데이터가 없습니다. 구글 시트를 확인해주세요.")
else:
    # --- CSS 및 메인 페이지 콘텐츠 ---
    st.markdown("""
    <style>
    /* 폰트 설정 (app.py의 폰트 설정과 동일하게 유지) */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Batang&family=Noto+Serif+KR:wght@200..900&family=Orbit&family=Poor+Story&display=swap');
    html, body, [class*="css"] {
        font-family: 'Orbit', sans-serif !important;
    }
    * {
        font-family: 'Orbit', sans-serif !important;
    }

    /* 버튼 스타일 - 최소한의 설정만 남기고 Streamlit 테마를 따르게 함 */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        /* background-color, color, border 등은 Streamlit 테마가 관리 */
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        transition: none; /* 트랜지션 효과도 제거하여 Streamlit 기본 동작 따름 */
    }
    /* 호버, 클릭 시 스타일도 Streamlit 테마에 맡김. 불필요한 부분 제거 */
    /* .stButton>button:hover { ... } */
    /* .stButton>button:active { ... } */


    /* 정보 박스 스타일 */
    .info-box {
        background-color: #f0f2f6; /* Streamlit light background */
        border-left: 5px solid #4CAF50; /* Green border */
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


    # 필터링 및 정렬을 위한 공간 분할 (두 개의 컬럼)
    col1, col2 = st.columns([2, 1])

    with col2:
        with st.container(border=True):
            st.markdown("""
            <div class="info-box">
                <p>💡 <strong>데이터 업데이트 주기:</strong></p>
                <p>이 앱의 데이터는 매 24시간마다 자동으로 반영됩니다.</p>
                <br>
                <p>혹시 어제 맛집에 다녀오셨나요?</p>
                <p>아래 링크에서 선생님의 맛집을 공유해주세요!</p>
                <p>정보에 오류가 있다면 수정해주세요^^</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.link_button("구글 시트 원본 바로 가기 ➡️", GOOGLE_SHEET_EDIT_URL, help="새 탭에서 구글 시트 원본을 엽니다.")


        st.markdown("---")
        
        st.header("나에게 맞는 식당 찾기 ✨")

        if 'filter_option' not in st.session_state:
            st.session_state.filter_option = 'None'

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("주차 걱정 No! 🅿️", help="주차 난이도 '하'인 식당을 우선적으로 보여줍니다."):
                st.session_state.filter_option = 'parking_easy'
        
        with btn_col2:
            if st.button("학교와의 거리순 🚶‍♀️", help="학교에서 가까운 순서대로 정렬합니다."):
                st.session_state.filter_option = 'distance_sort'

        if st.button("모든 필터/정렬 해제 🔄", help="모든 필터 및 정렬을 해제하고 초기 상태로 돌아갑니다."):
            st.session_state.filter_option = 'None'

        filtered_df = df.copy()

        if st.session_state.filter_option == 'parking_easy':
            if '주차난이도' in filtered_df.columns:
                parking_order = {'하': 0, '중': 1, '상': 2, None: 3}
                filtered_df['parking_sort_key'] = filtered_df['주차난이도'].fillna(None).map(parking_order)
                filtered_df = filtered_df.sort_values(by='parking_sort_key', ascending=True).drop(columns='parking_sort_key')
            else:
                st.warning("CSV 파일에 '주차난이도' 컬럼이 없어 주차 필터를 적용할 수 없습니다.")
        elif st.session_state.filter_option == 'distance_sort':
            if '거리(km)' in filtered_df.columns:
                filtered_df = filtered_df.sort_values(by='거리(km)', ascending=True)
            else:
                st.warning("CSV 파일에 '거리(km)' 컬럼이 없어 거리순 정렬을 적용할 수 없습니다.")

    with col1:
        st.subheader("📍 지도에서 식당 위치 확인")

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

            folium.Marker(
                location=[JUYEOP_SCHOOL_LAT, JUYEOP_SCHOOL_LON],
                popup=folium.Popup("<strong>주엽고등학교</strong>", max_width=150),
                tooltip="주엽고등학교",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)

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
                    ).add_to(m)

        folium_static(m, width=800, height=500)

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
