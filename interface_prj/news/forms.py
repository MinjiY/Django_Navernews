from django import forms

class NameForm(forms.Form):
    news_title = forms.CharField(label='Search keyword', max_length=7)