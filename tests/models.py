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