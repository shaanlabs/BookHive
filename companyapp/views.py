from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Book, BorrowTransaction
from .forms import BookForm, BookBulkImportForm, MemberCreateForm
import json
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def homefunction(request):
    return render(request,"companyapp/index.html")

@login_required
def dashboard(request):
    # Quick Issue/Return logic
    if request.method == 'POST':
        action = request.POST.get('action')
        book_id = request.POST.get('book_id')
        member_id = request.POST.get('member_id')
        if action == 'issue' and book_id and member_id:
            book = Book.objects.get(id=book_id)
            member = User.objects.get(id=member_id)
            if book.copies_available > 0:
                BorrowTransaction.objects.create(
                    book=book,
                    user=member,
                    due_date=timezone.now().date() + timezone.timedelta(days=14),
                    status='borrowed',
                )
                book.copies_available -= 1
                book.save()
                messages.success(request, f'Book "{book.title}" issued to {member.username}.')
            else:
                messages.error(request, f'No copies available for "{book.title}".')
        elif action == 'return' and book_id and member_id:
            tx = BorrowTransaction.objects.filter(book_id=book_id, user_id=member_id, status='borrowed').first()
            if tx:
                tx.status = 'returned'
                tx.return_date = timezone.now().date()
                tx.save()
                book = tx.book
                book.copies_available += 1
                book.save()
                messages.success(request, f'Book "{book.title}" returned by {tx.user.username}.')
            else:
                messages.error(request, 'No active borrowing found for this book and member.')

    total_books = Book.objects.count()
    available_books = Book.objects.filter(copies_available__gt=0).count()
    active_borrowings = BorrowTransaction.objects.filter(status='borrowed').count()
    overdue_books = BorrowTransaction.objects.filter(status='overdue').count()

    # Books per genre (pie chart)
    genre_data = Book.objects.values('genre').annotate(count=Count('id')).order_by('genre')
    genre_labels = [Book.GENRE_CHOICES_DICT.get(g['genre'], g['genre'].title()) for g in genre_data]
    genre_counts = [g['count'] for g in genre_data]

    # Books added per month (last 6 months, line chart)
    today = timezone.now().date()
    months = []
    books_line_counts = []
    for i in range(5, -1, -1):
        month = (today.replace(day=1) - timezone.timedelta(days=30*i)).replace(day=1)
        label = month.strftime('%b %Y')
        months.append(label)
        count = Book.objects.filter(date_added__year=month.year, date_added__month=month.month).count()
        books_line_counts.append(count)

    # Book availability (doughnut chart)
    checked_out = BorrowTransaction.objects.filter(status='borrowed').count()
    availability_labels = ['Available', 'Checked Out']
    availability_counts = [available_books, checked_out]

    # Top 5 most borrowed books (bar chart)
    top_books_qs = BorrowTransaction.objects.values('book__title').annotate(borrow_count=Count('id')).order_by('-borrow_count')[:5]
    top_books_labels = [b['book__title'] for b in top_books_qs]
    top_books_counts = [b['borrow_count'] for b in top_books_qs]

    # Overdue books table
    overdue_list = BorrowTransaction.objects.filter(status='overdue').select_related('book', 'user')

    # Activity feed (last 10 borrow/return actions)
    activity_feed = BorrowTransaction.objects.select_related('book', 'user').order_by('-issue_date', '-return_date')[:10]

    # Quick Issue/Return panel data
    available_books_list = Book.objects.filter(copies_available__gt=0)
    members = User.objects.filter(groups__name='Member') | User.objects.filter(groups__name='Librarian')

    context = {
        'total_books': total_books,
        'available_books': available_books,
        'active_borrowings': active_borrowings,
        'overdue_books': overdue_books,
        'genre_labels': json.dumps(genre_labels),
        'genre_counts': json.dumps(genre_counts),
        'books_line_labels': json.dumps(months),
        'books_line_counts': json.dumps(books_line_counts),
        'availability_labels': json.dumps(availability_labels),
        'availability_counts': json.dumps(availability_counts),
        'top_books_labels': json.dumps(top_books_labels),
        'top_books_counts': json.dumps(top_books_counts),
        'overdue_list': overdue_list,
        'activity_feed': activity_feed,
        'available_books_list': available_books_list,
        'members': members.distinct(),
    }
    return render(request, 'companyapp/dashboard.html', context)

@login_required
def send_overdue_emails(request):
    overdue_txs = BorrowTransaction.objects.filter(status='overdue').select_related('user', 'book')
    for tx in overdue_txs:
        if tx.user.email:
            send_mail(
                subject='Library Overdue Book Reminder',
                message=f'Dear {tx.user.username},\n\nThe book "{tx.book.title}" is overdue. Please return it as soon as possible.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[tx.user.email],
                fail_silently=True,
            )
    messages.success(request, 'Overdue email notifications sent!')
    return redirect('dashboard')

@login_required
def export_books_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="books.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Author', 'Genre', 'ISBN', 'Publisher', 'Copies Available', 'Shelf Location'])
    for book in Book.objects.all():
        writer.writerow([
            book.title, book.author, book.get_genre_display(), book.isbn, book.publisher, book.copies_available, book.shelf_location
        ])
    return response

@login_required
def export_borrowings_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="borrowings.csv"'
    writer = csv.writer(response)
    writer.writerow(['Book', 'User', 'Issue Date', 'Due Date', 'Return Date', 'Status'])
    for tx in BorrowTransaction.objects.select_related('book', 'user').all():
        writer.writerow([
            tx.book.title, tx.user.username, tx.issue_date, tx.due_date, tx.return_date, tx.status
        ])
    return response

@login_required
def export_overdue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="overdue_books.csv"'
    writer = csv.writer(response)
    writer.writerow(['Book', 'User', 'Due Date'])
    for tx in BorrowTransaction.objects.filter(status='overdue').select_related('book', 'user'):
        writer.writerow([
            tx.book.title, tx.user.username, tx.due_date
        ])
    return response

@login_required
def member_management(request):
    query = request.GET.get('q', '')
    members = User.objects.filter(Q(groups__name='Member') | Q(groups__name='Librarian')).distinct()
    if query:
        members = members.filter(Q(username__icontains=query) | Q(email__icontains=query))
    context = {
        'members': members,
        'query': query,
    }
    return render(request, 'companyapp/member_management.html', context)

@login_required
def add_member(request):
    if request.method == 'POST':
        form = MemberCreateForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User, Group
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                group = Group.objects.get(name=role)
                user.groups.add(group)
                messages.success(request, f'{role} "{username}" created successfully!')
                return redirect('member-management')
    else:
        form = MemberCreateForm()
    return render(request, 'companyapp/add_member.html', {'form': form})

def guest_login(request):
    user = authenticate(request, username='guest', password='guest1234')
    if user is not None:
        login(request, user)
        return redirect('dashboard')
    else:
        # Optionally, create the guest user if it doesn't exist
        from django.contrib.auth.models import User
        if not User.objects.filter(username='guest').exists():
            User.objects.create_user(username='guest', password='guest1234')
            user = authenticate(request, username='guest', password='guest1234')
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        return redirect('login')

class BookListView(ListView):
    model = Book
    template_name = 'companyapp/book_list.html'
    context_object_name = 'books'
    paginate_by = 10

class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'companyapp/book_form.html'
    success_url = reverse_lazy('book-list')

class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'companyapp/book_form.html'
    success_url = reverse_lazy('book-list')

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'companyapp/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return HttpResponseRedirect(f'{self.success_url}?deleted=1')

@login_required
def bulk_import_books(request):
    import csv
    from io import TextIOWrapper
    summary = {'imported': 0, 'errors': []}
    if request.method == 'POST':
        form = BookBulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    Book.objects.create(
                        title=row['title'],
                        author=row['author'],
                        genre=row['genre'],
                        isbn=row['isbn'],
                        publisher=row['publisher'],
                        copies_available=int(row['copies_available']),
                        shelf_location=row['shelf_location'],
                    )
                    summary['imported'] += 1
                except Exception as e:
                    summary['errors'].append(f"Row {reader.line_num}: {e}")
            messages.success(request, f"Imported {summary['imported']} books.")
            if summary['errors']:
                messages.error(request, f"Errors: {'; '.join(summary['errors'])}")
            return redirect('dashboard')
    else:
        form = BookBulkImportForm()
    return render(request, 'companyapp/bulk_import_books.html', {'form': form})