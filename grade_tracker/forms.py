from django.forms import ModelForm
from grade_tracker.models import MataKuliah, KomponenPenilaian
from django.utils.html import strip_tags

class MataKuliahForm(ModelForm):
    class Meta:
        model = MataKuliah
        fields = ["nama", "sks"]

    def clean_nama(self):
        nama = self.cleaned_data["nama"]
        return strip_tags(nama)

class KomponenPenilaianForm(ModelForm):
    class Meta:
        model = KomponenPenilaian
        fields = ["nama", "persentase"]
    
    def clean_nama(self):
        nama = self.cleaned_data["nama"]
        return strip_tags(nama)