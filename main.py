import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# 학교 주소
school_address = "경기도 고양시 일산서구 킨텍스로 341"

# 구글시트 csv URL
gsheet_url = "https://docs.google.com/spreadsheets/d/1YxB2y-Vvfyk3AKPR8zCYZgldDnAdk_aeaLqbl25Ye34/export?format=csv"
df = pd.read_csv(gsheet_url)
df.columns = df.columns.str.strip()

st.title("우리 학교 근처 회식장소 모음")

# 1. 학교 위치 위도/경도 얻기 (최초 한 번만)
@st.cache_data
def get_latlng(address):
    geolocator = Nominatim(user_agent="school_locator")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

school_lat, school_lng = get_latlng(school_address)

# 2. 각 식당 주소 → 위도/경도 변환 (혹시 주소가 많으면 시간 좀 걸림)
def get_latlng_row(address):
    geolocator = Nominatim(user_agent="store_locator")
    location = geolocator.geocode(address)
    if location:
        return pd.Series({'lat': location.latitude, 'lng': location.longitude})
    else:
        return pd.Series({'lat': None, 'lng': None})

# 주소 → 위경도 변환 (캐싱)
@st.cache_data
def add_latlng_columns(df):
    temp_df = df.copy()
    latlngs = temp_df['주소'].apply(get_latlng_row)
    temp_df = pd.concat([temp_df, latlngs], axis=1)
    return temp_df

df = add_latlng_columns(df)

# 3. 거리 계산
def calc_distance(row):
    if pd.notnull(row['lat']) and pd.notnull(row['lng']) and school_lat and school_lng:
        return geodesic((school_lat, school_lng), (row['lat'], row['lng'])).km
    else:
        return None

df['학교와_거리_km'] = df.apply(calc_distance, axis=1)
df['학교와_거리_km'] = df['학교와_거리_km'].apply(lambda x: round(x, 2) if pd.notnull(x) else "알 수 없음")

# 4. 페이지 내 필터 UI
col1, col2, col3 = st.columns(3)
with col1:
    food_types = st.multiselect('음식종류', sorted(df['음식종류'].dropna().unique()))
with col2:
    parking = st.multiselect('주차난이도', sorted(df['주차난이도'].dropna().unique()))
with col3:
    holiday = st.multiselect('휴무', sorted(df['휴무'].dropna().unique()))

filtered = df.copy()
if food_types:
    filtered = filtered[filtered['음식종류'].isin(food_types)]
if parking:
    filtered = filtered[filtered['주차난이도'].isin(parking)]
if holiday:
    filtered = filtered[filtered['휴무'].isin(holiday)]

st.subheader("회식장소 리스트 (학교와 거리 표시)")
st.dataframe(filtered[['이름', '주소', '음식종류', '주차난이도', '휴무', '오픈시간', '학교와_거리_km']], use_container_width=True)

# 상세 정보
for idx, row in filtered.iterrows():
    st.markdown(f"---\n### {row['이름']}")
    st.write(f"**주소:** {row['주소']}")
    st.write(f"**연락처:** {row['연락처']}")
    st.write(f"**음식종류:** {row['음식종류']}")
    st.write(f"**주차난이도:** {row['주차난이도']}")
    st.write(f"**휴무:** {row['휴무']}  |  **오픈시간:** {row['오픈시간']}")
    st.write(f"**학교와 거리:** {row['학교와_거리_km']} km")

