from django.db import models

# Create your models here.
class Initiative(models.Model):
	ag_id = models.CharField(max_length=10)
	id_note = models.CharField(max_length=50)
	sos_id = models.CharField(max_length=10)
	title = models.CharField(max_length=999)
	summary = models.CharField(max_length=9999)
	proponent = models.CharField(max_length=200)
	email = models.CharField(max_length=200)
	phone = models.CharField(max_length=20)
	sum_date = models.DateTimeField('Summary Date')
	status = models.CharField(max_length=20)
	deadline = models.DateTimeField('Deadline')
	sig_req = models.IntegerField(default=0)