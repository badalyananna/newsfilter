from django import forms
from .models import Website, Topic, NewsPiece

class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['name', 'rss']

class TopicForm(forms.ModelForm):
    ignor_words = forms.CharField(widget = forms.Textarea, required=False)
    class Meta:
        model = Topic
        fields = ['name', 'key_words', 'ignor_words']

class NewsPieceTopicForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """ Grants access to the User object so that only topics of the current user
        are given as options"""

        self.user = kwargs.pop('user')
        super(NewsPieceTopicForm, self).__init__(*args, **kwargs)
        self.fields['topics_assigned'].queryset = Topic.objects.filter(user=self.user)
    
    class Meta:
        model = NewsPiece
        fields = ['topics_assigned']
    
    

    topics_assigned = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple, required=False)
