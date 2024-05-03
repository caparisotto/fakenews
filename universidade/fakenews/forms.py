from django import forms
from django.forms import ModelForm, Textarea, ChoiceField

#CHOICES=(
#('1', 'FRASE'),
#('2', 'PALAVRAS'),
#)


class FormFrase(forms.Form):
    texto = forms.CharField(label="Digite/Copie a frase que deseja analisar", max_length=100000)
    texto.widget = forms.TextInput(attrs={'size': 100, 'title': 'Search',})

