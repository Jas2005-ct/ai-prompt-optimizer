from django.contrib import admin
from .models import PromptTemplate

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'use_count']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'template_text']
