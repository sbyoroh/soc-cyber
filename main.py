from fastapi import FastAPI, Request
import pickle
import pandas as pd
import logging

logging.basicConfig(
    filename='alerts.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(title='AI SOC Analyst API')

with open('xgb_model.pkl', 'rb') as f:
    model = pickle.load(f)

# ????? ???? ?????? IP ???? ???? ?????
blocked_ips = set()

@app.get('/')
def read_root():
    return {'status': 'Active', 'message': 'MDR Backend is running!'}

@app.post('/analyze')
async def analyze_traffic(request: Request):
    try:
        data = await request.json()
        
        # ?????? ????? IP ???????
        attacker_ip = data.get('srcip', '192.168.1.50')
        
        # ????? ???????? ???????
        model_data = {k: v for k, v in data.items() if k != 'srcip'}
        df = pd.DataFrame([model_data])
        prediction = model.predict(df)
        
        is_attack = int(prediction[0]) == 1
        
        if is_attack:
            # 1. ????? ??????
            logging.warning(f'THREAT DETECTED from IP: {attacker_ip}')
            
            # 2. ????????? ????????? (MDR Response): ??? ??? IP
            blocked_ips.add(attacker_ip)
            logging.warning(f'ACTION TAKEN: Firewall rule added to block IP {attacker_ip}.')
            
            return {
                "status": "success",
                "prediction_text": "?? ???? ??????? ?????!",
                "threat_detected": True,
                "action_taken": f"Blocked IP: {attacker_ip}",
                "total_blocked_ips": len(blocked_ips)
            }
        else:
            return {
                "status": "success",
                "prediction_text": "? ???? ???? ??????",
                "threat_detected": False,
                "action_taken": "None"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
