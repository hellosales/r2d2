from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify

from r2d2.notifications.signals import notification_post_save

from r2d2.accounts.models import Account


class Category (models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        return super(Category, self).save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(Account, related_name="notifications")
    category = models.ForeignKey(Category, related_name='notifications')
    created = models.DateField(auto_now_add=True)
    content = models.TextField()
    subject = models.TextField()
    title = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    is_sent = models.BooleanField(default=False, help_text="Uncheck and save to resend")
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        index_together = [
            ['user', 'is_sent', 'is_read']
        ]

    def as_dict(self):
        return {
            'user_id': self.user.id,
            'user': self.user,
            'category': self.category,
            'content': self.content,
            'subject': self.subject,
            'url': self.url,
            'is_sent': self.is_sent,
            'is_read': self.is_read,
            'title': self.title,
        }

    def __unicode__(self):
        return '%s, %s, send: %s' % (self.subject, self.category, str(self.is_sent))

post_save.connect(notification_post_save, sender=Notification)
