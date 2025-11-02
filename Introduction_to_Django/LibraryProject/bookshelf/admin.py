from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Fields shown in the list page
    list_display = ('title', 'author', 'publication_year')
    
    # Add filters on the right side
    list_filter = ('publication_year', 'author')
    
    # Add search bar for title and author
    search_fields = ('title', 'author')
