from jnius import autoclass
from android import mActivity
from android.runnable import run_on_ui_thread

Service = autoclass('android.app.Service')
Intent = autoclass('android.content.Intent')
Context = autoclass('android.content.Context')
PythonService = autoclass('org.kivy.android.PythonService')

class BackgroundService(Service):
    @run_on_ui_thread
    def onCreate(self):
        super().onCreate()
        self.startForegroundService()

    def startForegroundService(self):
        # Create notification channel (required for Android 8+)
        self.create_notification_channel()
        
        # Build notification
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        builder = NotificationBuilder(mActivity, "background_channel")
        
        builder.setContentTitle("Background Service")
        builder.setContentText("Running in background")
        builder.setSmallIcon(mActivity.getResources().getIdentifier(
            "icon", "drawable", mActivity.getPackageName()))
        builder.setOngoing(True)
        
        # Start foreground service
        notification = builder.build()
        self.startForeground(1, notification)

    def create_notification_channel(self):
        if autoclass('android.os.Build$VERSION').SDK_INT >= 26:
            NotificationManager = autoclass('android.app.NotificationManager')
            NotificationChannel = autoclass('android.app.NotificationChannel')
            
            channel = NotificationChannel(
                "background_channel",
                "Background Service",
                NotificationManager.IMPORTANCE_LOW
            )
            
            notification_manager = mActivity.getSystemService(Context.NOTIFICATION_SERVICE)
            notification_manager.createNotificationChannel(channel)

    def onBind(self, intent):
        return None

# Service starter
def start_service():
    service_intent = Intent(mActivity, BackgroundService)
    mActivity.startService(service_intent)
