from jnius import autoclass
from android.runnable import run_on_ui_thread

Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
NotificationBuilder = autoclass('android.app.Notification$Builder')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

class BackgroundService:
    @classmethod
    @run_on_ui_thread
    def start(cls):
        activity = PythonActivity.mActivity
        service_intent = Intent(activity, cls.get_service_class())
        activity.startService(service_intent)

    @classmethod
    def get_service_class(cls):
        class Service(autoclass('android.app.Service')):
            def onCreate(self):
                super().onCreate()
                self.setup_foreground_service()

            def setup_foreground_service(self):
                if autoclass('android.os.Build$VERSION').SDK_INT >= 26:
                    self.create_notification_channel()
                
                builder = NotificationBuilder(self, "background_channel")
                builder.setContentTitle("Background Service")
                builder.setContentText("Running in background")
                builder.setSmallIcon(self.get_resources().getIdentifier(
                    "icon", "drawable", self.getPackageName()))
                builder.setOngoing(True)
                self.startForeground(1, builder.build())

            def create_notification_channel(self):
                channel = NotificationChannel(
                    "background_channel",
                    "Background Service",
                    NotificationManager.IMPORTANCE_LOW
                )
                manager = self.getSystemService(Context.NOTIFICATION_SERVICE)
                manager.createNotificationChannel(channel)

            def onBind(self, intent):
                return None

        return Service
