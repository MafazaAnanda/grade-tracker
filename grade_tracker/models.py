from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class MataKuliah(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    nama = models.CharField(max_length=100)
    sks = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.nama
    
    @property
    def total_nilai(self):
        semua_komponen = self.semua_komponen.all()
        total = 0
        for komponen in semua_komponen:
            total += (komponen.nilai * komponen.persentase) / 100 

        return round(total, 2)
    
class Penilaian(models.Model):
    mata_kuliah = models.ForeignKey(
        MataKuliah, 
        related_name="semua_komponen", 
        on_delete=models.CASCADE
    )
    nama = models.CharField(max_length=100)
    persentase = models.FloatField(
        validators=[
            MinValueValidator(0), 
            MaxValueValidator(100)
        ]
    )
    nilai = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    deadline = models.DateTimeField(null=True, blank=True)
    sudah_selesai = models.BooleanField(default=False)
    notifikasi_email = models.BooleanField(default=False)

    def __str__(self):
        return f" {self.nama} - {self.mata_kuliah}"