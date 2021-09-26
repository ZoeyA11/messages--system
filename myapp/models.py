from django.contrib.auth.models import User

from django.db import models


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recieved_messages')
    subject = models.CharField(max_length=200, blank=False, default='')
    message = models.CharField(max_length=200, blank=False, default='')
    date_created = models.DateField(auto_now_add=True)
    reciever_read_message = models.BooleanField(default=False)

    def __str__(self):
        return "{subject}:{message}".format(subject=self.subject, message=self.message)
