from django.forms import ModelForm
from .models import User

class EditUserForm(ModelForm):
    class Meta:
        model=User
        fields=["username", "email", "first_name", "last_name"]
        