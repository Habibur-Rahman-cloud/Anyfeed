from django import forms
from .models import CustomUser

class UserDashboardForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
