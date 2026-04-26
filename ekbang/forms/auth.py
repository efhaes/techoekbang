from django import forms
from django.contrib.auth.models import User
from ekbang.models import UserProfile, Desa

class DesaForm(forms.ModelForm):
    class Meta:
        model = Desa
        fields = ['nama', 'kecamatan']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'kecamatan': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class BuatAkunDesaForm(forms.ModelForm):
    # TAMBAHKAN FIELD EMAIL
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contoh: desa.suka@gmail.com'})
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    konfirmasi_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    desa = forms.ModelChoiceField(
        queryset=Desa.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password'] # Masukkan email ke sini

    # Tambahkan validasi password agar tidak salah ketik
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        konfirmasi = cleaned_data.get("konfirmasi_password")

        if password != konfirmasi:
            raise forms.ValidationError("Password dan Konfirmasi Password tidak cocok!")
        return cleaned_data