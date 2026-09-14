from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["soc_database"]
alerts = db["security_alerts"]
print(f"Total recorded attacks in the database: {alerts.count_documents({})}")
print("-" * 50)

for alert in alerts.find():
    print(f"Time: {alert['timestamp']} | IP: {alert['ip_address']} | Threat: {alert['threat_type']} | Action: {alert['action_taken']}")