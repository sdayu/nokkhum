
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib

from nokkhum import config, models


class EmailNotification:

    def __init__(self):
        settings = config.settings

        self.mailer = smtplib.SMTP(settings.get("nokkhum.smtp.host"),
                                   settings.get("nokkhum.smtp.port"))

        if settings.get("nokkhum.smtp.tls"):
            self.mailer.starttls()

        self.mailer.login(
            settings.get('nokkhum.smtp.username'), settings.get('nokkhum.smtp.password'))
        self.sender = settings.get('nokkhum.smtp.username')

    def send_mail(self, camera_id):

        camera = models.Camera.objects(id=camera_id).first()

        subject = "Some thing wrong in system"
        body = "FYI camera id: %d name: %s \n" % (camera.id, camera.name)

        message = MIMEMultipart()
        message['From'] = self.sender
        message['To'] = camera.owner.email
        message['Subject'] = subject

        message.attach(MIMEText(body))

        self.mailer.sendmail(
            self.sender, camera.owner.email, message.as_string())

    def __del__(self):
        pass
        # self.mailer.close()
