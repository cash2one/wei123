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
    poster_id = models.IntegerField(primary_key=True)
    poster_b64 = models.CharField(max_length=100)
    poster_name = models.CharField(max_length=100)
    poster_last_thread = models.IntegerField()

class weixin_article_info(models.Model):
    id = models.CharField(primary_key=True, max_length=500)
    fileid = models.IntegerField()
    mid = models.IntegerField()
    datetime = models.IntegerField()
    title = models.CharField(max_length=500)
    content_url = models.CharField(max_length=500)
    cover_url = models.CharField(max_length=500)
    poster_id = models.ForeignKey(weixin_poster, related_name='weixin_poster_articles')
    
    # controller
    is_display = models.BooleanField()
    
class weixin_requester(models.Model):
    requester_uin = models.CharField(max_length=100)
    requester_key = models.CharField(max_length=200)

class common_status(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
