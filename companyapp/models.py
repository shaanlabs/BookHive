from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

# Create your models here.

class Book(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('nonfiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('other', 'Other'),
    ]
    GENRE_CHOICES_DICT = dict(GENRE_CHOICES)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    copies_available = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BorrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='borrowed')

    def __str__(self):
        return f"{self.book.title} to {self.user.username} ({self.status})"

# Signal to create groups for roles if they don't exist
@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    for role in ['Admin', 'Librarian', 'Member']:
        Group.objects.get_or_create(name=role)
