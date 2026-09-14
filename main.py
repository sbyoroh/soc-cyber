from fastapi import FastAPI, Request
import pickle
import pandas as pd
import logging
import datetime
from pymongo import MongoClient
import subprocess
import threading

# إعداد تسجيل الأخطاء
logging.basicConfig(
    filename='alerts.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(title='AI SOC Analyst API & IPS')

# إعداد قاعدة البيانات
client = MongoClient("mongodb://localhost:27017/")
db = client["soc_database"]
collection = db["security_alerts"]

# تحميل النموذج المصغر
try:
    with open('xgb_model_light.pkl', 'rb') as f:
        model = pickle.load(f)
    print("✅ AI Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Error loading model: {e}")
    model = None

blocked_ips = set()

def block_ip_windows(ip_address):
    """دالة تتصل بجدار حماية الويندوز لحظر الـ IP فعلياً"""
    # حماية: لا تحظر أبداً الشبكة المحلية أو الـ Localhost
    if ip_address.startswith("192.168.") or ip_address == "127.0.0.1":
        return

    if ip_address not in blocked_ips:
        command = f'netsh advfirewall firewall add rule name="SOC_BLOCK_{ip_address}" dir=in action=block remoteip={ip_address}'
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            blocked_ips.add(ip_address)
            logging.warning(f'FIREWALL ACTION: Successfully blocked IP {ip_address}')
            print(f"\n[🛡️ IPS FIREWALL] Successfully BLOCKED {ip_address} in Windows!")
        except Exception as e:
            logging.error(f'Failed to block IP {ip_address}: {e}')
# قائمة الـ Whitelist الابتدائية
whitelist_ips = {"127.0.0.1", "192.168.1.1"}

@app.post("/whitelist/add")
async def add_to_whitelist(request: Request):
    data = await request.json()
    ip = data.get("ip_address")
    if ip:
        whitelist_ips.add(ip)
        return {"status": "Success", "message": f"IP {ip} added to whitelist successfully."}
    return {"status": "Error", "message": "Invalid IP address."}

@app.get("/whitelist/list")
async def get_whitelist():
    return {"whitelist": list(whitelist_ips)}
@app.get('/')
def read_root():
    return {'status': 'Active', 'message': 'MDR Backend with AI & IPS is running!'}

@app.post("/detect/")
async def detect_threat(request: Request):
    data = await request.json()
    ip = data.get("ip_address", "Unknown")
    
    # حماية الآيبيهات المحلية من الحظر
    is_local = ip.startswith("192.168.") or ip == "127.0.0.1"
    is_attack = False
    
    # استخدام الذكاء الاصطناعي للتنبؤ
    if model is not None:
        # تجهيز البيانات بنفس الأسماء التي تدرب عليها الموديل
        df_features = pd.DataFrame([{
            'spkts': data.get('spkts', 0),
            'sbytes': data.get('sbytes', 0),
            'rate': data.get('rate', 0.0)
        }])
        prediction = model.predict(df_features)
        
        # إذا كانت نتيجة الذكاء الاصطناعي = 1 (هجوم)
        if int(prediction[0]) == 1:
            is_attack = True

    # إذا اكتشف الـ AI هجوماً والـ IP ليس محلياً
    if is_attack and not is_local:
        threading.Thread(target=block_ip_windows, args=(ip,)).start()
        
        if ip not in blocked_ips:
            alert = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip_address": ip,
                "threat_type": "AI_Detected_Threat",
                "action_taken": "Firewall Blocked"
            }
            collection.insert_one(alert)
            
        return {"status": "Malicious", "action": "Blocked"}
        
    return {"status": "Safe", "action": "None"}