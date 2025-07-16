from django.db import models
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

class Book(models.Model):
    """Represents a book in the library."""
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
    title = models.CharField(max_length=255, help_text="Title of the book.")
    author = models.CharField(max_length=255, help_text="Author of the book.")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, help_text="Genre of the book.")
    isbn = models.CharField(max_length=13, unique=True, help_text="ISBN number.")
    publisher = models.CharField(max_length=255, help_text="Publisher of the book.")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, help_text="Book cover image.")
    copies_available = models.PositiveIntegerField(default=1, help_text="Number of available copies.")
    shelf_location = models.CharField(max_length=100, help_text="Shelf location in the library.")
    date_added = models.DateTimeField(auto_now_add=True, help_text="Date the book was added.")

    def __str__(self):
        return self.title

    def is_available(self):
        """Returns True if at least one copy is available."""
        return self.copies_available > 0

class BorrowTransaction(models.Model):
    """Represents a borrowing transaction for a book."""
    STATUS_BORROWED = 'borrowed'
    STATUS_RETURNED = 'returned'
    STATUS_OVERDUE = 'overdue'
    STATUS_CHOICES = [
        (STATUS_BORROWED, 'Borrowed'),
        (STATUS_RETURNED, 'Returned'),
        (STATUS_OVERDUE, 'Overdue'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrow_transactions')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_BORROWED)

    def __str__(self):
        return f"{self.book.title} to {self.user.username} ({self.status})"

    def is_overdue(self):
        """Returns True if the book is overdue and not yet returned."""
        from django.utils import timezone
        return self.status == self.STATUS_BORROWED and self.due_date < timezone.now().date()

    def mark_returned(self):
        """Mark this transaction as returned."""
        from django.utils import timezone
        self.status = self.STATUS_RETURNED
        self.return_date = timezone.now().date()
        self.save()
        self.book.copies_available += 1
        self.book.save()

    def mark_overdue(self):
        """Mark this transaction as overdue."""
        self.status = self.STATUS_OVERDUE
        self.save()

# Signal to create groups for roles if they don't exist
@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    """Ensure default user groups exist after migrations."""
    for role in ['Admin', 'Librarian', 'Member']:
        Group.objects.get_or_create(name=role)
