from django.db import models

# Create your models here.
class weixin_article(models.Model):
    post_title = models.CharField(max_length=100)
    post_link = models.CharField(max_length=100)
    post_user = models.CharField(max_length=100)
    post_date = models.CharField(max_length=100)
    
    def __unicode():
        return u'%s' % (post_title)
        
class weixin_poster(models.Model):
    post_user = models.CharField(max_length=100)
    post_last_thread = models.IntegerField()

class weixin_requester(models.Model):
    requester_uin = models.CharField(max_length=100)
    requester_key = models.CharField(max_length=200)

class common_status(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
