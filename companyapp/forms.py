from django import forms
from .models import Book
from django.contrib.auth.models import Group

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'isbn', 'publisher', 'cover_image', 'copies_available', 'shelf_location']

class BookBulkImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV File', help_text='Upload a CSV file with columns: title, author, genre, isbn, publisher, copies_available, shelf_location')

class MemberCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[('Member', 'Member'), ('Librarian', 'Librarian')]) 