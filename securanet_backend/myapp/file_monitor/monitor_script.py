import time
from datetime import datetime
import requests

def monitor_files():
    while True:
        response = requests.get('http://127.0.0.1:8000/api/file-logs/')
        data = response.json()
        
        print("\n=== File Monitoring Status ===")
        print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("Recent Changes:")
        
        for log in data:
            print(f"\nFile: {log['file_path']}")
            print(f"Change Type: {log['change_type']}")
            print(f"Risk Level: {log['risk_level']}")
            if log.get('recommendation'):
                print(f"Recommendation: {log['recommendation']}")
        
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    monitor_files()