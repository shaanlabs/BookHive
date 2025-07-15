
from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/add/', views.BookCreateView.as_view(), name='book-add'),
    path('books/import/', views.bulk_import_books, name='bulk-import-books'),
    path('books/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book-edit'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('guest-login/', views.guest_login, name='guest-login'),
    path('export/books/', views.export_books_csv, name='export-books-csv'),
    path('export/borrowings/', views.export_borrowings_csv, name='export-borrowings-csv'),
    path('export/overdue/', views.export_overdue_csv, name='export-overdue-csv'),
    path('send-overdue-emails/', views.send_overdue_emails, name='send-overdue-emails'),
    path('members/', views.member_management, name='member-management'),
    path('members/add/', views.add_member, name='add-member'),
    path('myapp/', views.homefunction, name='homeapp'),  # Optional legacy
    path('', lambda request: redirect('dashboard', permanent=False)),  # Root URL redirects to dashboard
]