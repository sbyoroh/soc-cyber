from scapy.all import sniff, IP, TCP, UDP
import requests
import time
from collections import defaultdict
import threading

API_URL = "http://127.0.0.1:8000/detect/"

# قاموس لتخزين إحصائيات كل IP
ip_stats = defaultdict(lambda: {"count": 0, "total_size": 0})
last_send_time = time.time()

def process_packet(packet):
    global last_send_time
    
    if IP in packet:
        ip_src = packet[IP].src
        packet_len = len(packet)
        
        # تجميع البيانات
        ip_stats[ip_src]["count"] += 1
        ip_stats[ip_src]["total_size"] += packet_len

    # النافذة الزمنية (3 ثواني)
    current_time = time.time()
    if current_time - last_send_time >= 3.0:
        stats_copy = dict(ip_stats)
        ip_stats.clear()
        last_send_time = current_time
        
        threading.Thread(target=send_aggregated_data, args=(stats_copy,)).start()

def send_aggregated_data(stats):
    for ip, stat in stats.items():
        if stat["count"] > 0:
            packet_rate = round(stat["count"] / 3.0, 2)
            
            # إعداد الداتا لتناسب موديل XGBoost المصغر
            data = {
                "ip_address": ip,
                "spkts": stat["count"],          # عدد الحزم (Source Packets)
                "sbytes": stat["total_size"],    # حجم البيانات (Source Bytes)
                "rate": packet_rate              # معدل النقل (Rate)
            }
            
            try:
                response = requests.post(API_URL, json=data, timeout=2)
                if response.json().get("status") == "Malicious":
                    print(f"[🚨 THREAT] {ip} detected by AI! Action: Blocked.")
                else:
                    print(f"[✓] {ip} is Safe. (Rate: {packet_rate} p/s)")
            except:
                pass

print("📡 Sniffing network traffic (AI Integrated Mode)... (Press Ctrl+C to stop)")
sniff(prn=process_packet, store=False)