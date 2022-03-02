from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'priority', 'due_date', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Write a short title',
                'maxlength': 255,
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Add more detail about this task',
                'rows': 4,
            }),
            'priority': forms.Select(),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
            }),
        }
        labels = {
            'due_date': 'Due date',
            'is_completed': 'Completed',
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title:
            raise forms.ValidationError('Title is required.')
        return title

    def clean_description(self):
        description = self.cleaned_data['description'].strip()
        if not description:
            raise forms.ValidationError('Description is required.')
        return description
