import streamlit as st
import pandas as pd
import pyodbc
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

from st_aggrid import AgGrid, GridOptionsBuilder


st.set_page_config(page_title="Olist Pro Analiz", layout="wide")

st.title("🚀 Olist E-Ticaret: Hibrit Yapay Zeka & Excel Grid")
st.markdown("Bu panel, **100.000+ veriyi** SQL Server'dan çeker, Yapay Zeka ile analiz eder ve interaktif tablolarla sunar.")
st.markdown("---")


@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-5JAIPMI\\SQLEXPRESS;"  
        "DATABASE=OlistEcommerce;"            
        "Trusted_Connection=yes;"
    )

conn = init_connection()


@st.cache_data
def get_data():
    query = """
    SELECT 
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        p.payment_value,
        c.customer_city,
        c.customer_state
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    """
    with conn.cursor() as cur:
        df = pd.read_sql(query, conn)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

with st.spinner('Veriler SQL ve AI Motorunda işleniyor...'):
    df_raw = get_data()


last_date = df_raw['order_purchase_timestamp'].max() + dt.timedelta(days=2)
rfm = df_raw.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (last_date - x.max()).days,
    'order_id': 'count',
    'payment_value': 'sum',
    'customer_city': 'first',
    'customer_state': 'first'
})
rfm.columns = ['recency', 'frequency', 'monetary', 'city', 'state']


st.subheader("📈 Yönetici Özeti")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Toplam Ciro", f"{rfm['monetary'].sum():,.0f} TL")
kpi2.metric("Toplam Müşteri", f"{rfm.shape[0]:,}")
kpi3.metric("Ortalama Sepet", f"{rfm['monetary'].mean():.2f} TL")
kpi4.metric("En Yüksek Sipariş", f"{rfm['monetary'].max():,.0f} TL")

st.markdown("---")


rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

seg_map = {
    r'[1-2][1-2]': 'Hibernating (Uykuda)',
    r'[1-2][3-4]': 'At Risk (Riskli)',
    r'[1-2]5': 'Can\'t Loose (Kaybedemeyiz)',
    r'3[1-2]': 'About to Sleep (Uyuyacak)',
    r'33': 'Need Attention (Dikkat)',
    r'[3-4][4-5]': 'Loyal Customers (Sadık)',
    r'41': 'Promising (Umut Vaat Eden)',
    r'51': 'New Customers (Yeni)',
    r'[4-5][2-3]': 'Potential Loyalists (Potansiyel)',
    r'5[4-5]': 'Champions (Şampiyonlar)'
}
rfm['Segment_Label'] = rfm['RF_SCORE'].replace(seg_map, regex=True)


rfm_log = rfm[['recency', 'frequency', 'monetary']].apply(np.log1p)
scaler = MinMaxScaler()
rfm_scaled = scaler.fit_transform(rfm_log)
kmeans = KMeans(n_clusters=4, random_state=42)
kmeans.fit(pd.DataFrame(rfm_scaled))
rfm['Cluster_ID'] = kmeans.labels_


st.subheader("⚔️ İnsan vs. Yapay Zeka Matrisi")
col_matrix, col_desc = st.columns([2, 1])
with col_matrix:
    cross_tab = pd.crosstab(rfm['Segment_Label'], rfm['Cluster_ID'])
    st.dataframe(cross_tab.style.background_gradient(cmap="Reds"), use_container_width=True)
with col_desc:
    st.info("Bu matris, Kural Tabanlı Segmentler ile Yapay Zeka Kümeleri arasındaki ilişkiyi gösterir.")


st.markdown("---")
st.subheader("📍 Müşteri Segmentasyon Haritası")
fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=rfm, x='recency', y='monetary', hue='Cluster_ID', palette='viridis', alpha=0.6, s=15, ax=ax)
st.pyplot(fig)


st.markdown("---")
st.subheader("🎛️ İnteraktif Veri Tablosu (Data Grid)")
st.info("Aşağıdaki arama kutusuna 'Champions', 'Rio', 'SP' gibi kelimeler yazarak tabloyu anında filtreleyebilirsin.")


search_term = st.text_input("🔎 Tabloda Ara:", "")


grid_data = rfm[['city', 'state', 'Segment_Label', 'Cluster_ID', 'recency', 'monetary']].reset_index()


gb = GridOptionsBuilder.from_dataframe(grid_data)
gb.configure_pagination(paginationAutoPageSize=True) 


gb.configure_default_column(
    groupable=True, 
    value=True, 
    enableRowGroup=True, 
    aggFunc='sum', 
    editable=True,
    filter=True,       
    floatingFilter=True 
)

gb.configure_selection('multiple', use_checkbox=True)


if search_term:
    gb.configure_grid_options(quickFilterText=search_term)

gridOptions = gb.build()

AgGrid(
    grid_data,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    height=500,
    width='100%',
    theme="streamlit", 
    allow_unsafe_jscode=True
)