from django.forms import ModelForm
from grade_tracker.models import MataKuliah, Penilaian
from django.utils.html import strip_tags

class MataKuliahForm(ModelForm):
    class Meta:
        model = MataKuliah
        fields = ["nama", "sks"]

    def clean_nama(self):
        nama = self.cleaned_data["nama"]
        return strip_tags(nama)

class PenilaianForm(ModelForm):
    class Meta:
        model = Penilaian
        fields = ["nama", "persentase"]
    
    def clean_nama(self):
        nama = self.cleaned_data["nama"]
        return strip_tags(nama)