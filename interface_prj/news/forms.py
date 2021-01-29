from django import forms

class NameForm(forms.Form):
    news_topic = forms.CharField(label='Topic keyword',max_length=10)
    news_title = forms.CharField(label='Search keyword', max_length=20)

#update, delete form
class UDForm(forms.Form):
    UD = forms.CharField(label='delete',max_length=10)