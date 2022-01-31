from django.db import models


class CkDocumentsDivisions(models.Model):
    division = models.CharField(max_length=124, db_collation='Cyrillic_General_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ck_documents_divisions'


class CkDocumentsLevels(models.Model):
    level = models.CharField(max_length=45, db_collation='Cyrillic_General_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ck_documents_levels'


class CkDocuments(models.Model):
    description = models.TextField(db_collation='Cyrillic_General_CI_AS', blank=True, null=True)
    link = models.CharField(max_length=255, db_collation='Latin1_General_100_CI_AS')
    level_id = models.IntegerField()
    division_id = models.IntegerField()
    theme_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ck_documents'