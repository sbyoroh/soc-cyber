import streamlit as st
from pymongo import MongoClient
import pandas as pd
import time

# إعداد صفحة لوحة التحكم
st.set_page_config(
    page_title="AI SOC & MDR Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# الاتصال بقاعدة بيانات MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["soc_database"]
    collection = db["security_alerts"]
except Exception as e:
    st.error(f"Database connection failed: {e}")

# العنوان الرئيسي ووصف النظام
st.title("🛡️ AI-Powered SOC & MDR Operations Center")
st.markdown("Real-time network traffic monitoring, threat detection via **XGBoost AI**, and automated **Windows Firewall IPS** response.")

# لوحة التحكم الجانبية
st.sidebar.header("⚙️ Control Panel")
auto_refresh = st.sidebar.checkbox("Enable Live Auto-Refresh", value=True)

# تخطيط الإحصائيات العلوية
metric_col1, metric_col2, metric_col3 = st.columns(3)

# جلب التنبيهات من قاعدة البيانات
try:
    alerts_cursor = collection.find().sort("_id", -1).limit(50)
    alerts_list = list(alerts_cursor)
    df = pd.DataFrame(alerts_list)
except Exception:
    df = pd.DataFrame()

# حساب الإحصائيات والمؤشرات
total_threats = len(df) if not df.empty else 0
unique_attackers = df["ip_address"].nunique() if not df.empty and "ip_address" in df.columns else 0

with metric_col1:
    st.metric(label="🚨 Total Detected Threats", value=total_threats)
with metric_col2:
    st.metric(label="🎯 Unique Attacker IPs", value=unique_attackers)
with metric_col3:
    st.metric(label="🛡️ MDR Status", value="Active & Blocking")

st.markdown("---")

# جدول عرض الهجمات الحية
st.subheader("🔴 Live Security Incidents & Firewall Actions")

if not df.empty:
    # تنسيق معرف قاعدة البيانات للعرض
    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)
    
    # اختيار الأعمدة المتاحة للعرض
    display_columns = [col for col in ["timestamp", "ip_address", "threat_type", "action_taken"] if col in df.columns]
    
    # عرض الجدول التفاعلي
    st.dataframe(df[display_columns], width='stretch')
else:
    st.info("ℹ️ No threats detected yet. The network is secure and monitored by AI.")

# قسم الرسوم البيانية والإحصائيات
if not df.empty and "threat_type" in df.columns:
    st.markdown("---")
    st.subheader("📊 Threat Statistics & Classification")
    threat_counts = df["threat_type"].value_counts()
    st.bar_chart(threat_counts)

# معلومات الشريط الجانبي
st.sidebar.markdown("---")
st.sidebar.info("System running with FastAPI, Scapy, XGBoost, and MongoDB.")

# حلقة التحديث التلقائي للداشبورد كل 3 ثواني
if auto_refresh:
    time.sleep(3)
    st.rerun()