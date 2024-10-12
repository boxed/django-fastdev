from django.db import models


class BaseModel(models.Model):
    name = models.CharField(max_length=255,primary_key=True)


class ModelWithValidFK(models.Model):
    name = models.CharField(max_length=255,primary_key=True)
    base_model = models.ForeignKey(BaseModel,on_delete=models.CASCADE)


class ModelWithInvalidFK_id1(models.Model):
    base_model_id = models.ForeignKey(BaseModel,on_delete=models.CASCADE)


class ModelWithInvalidFK_ID2(models.Model):
    base_model_ID = models.ForeignKey(BaseModel,on_delete=models.CASCADE)


class ModelWithInvalidFK_iD3(models.Model):
    base_model_iD = models.ForeignKey(BaseModel,on_delete=models.CASCADE)


class ModelWithInvalidFKID4(models.Model):
    base_modelID = models.ForeignKey(BaseModel,on_delete=models.CASCADE)


class ModelWithInvalidFKId5(models.Model):
    base_modelId = models.ForeignKey(BaseModel,on_delete=models.CASCADE)


class ModelWithInvalidFKiD6(models.Model):
    base_modeliD = models.ForeignKey(BaseModel,on_delete=models.CASCADE)


class SelfRef(models.Model):
    selfref = models.ForeignKey('self', null=True, blank=True, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        return SelfRef.objects.get(selfref=self).pk

    # def __repr__(self):
    #     return f'<{type(self)} pk={self.pk}>'
