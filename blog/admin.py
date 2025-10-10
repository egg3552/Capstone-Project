from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, UserProfile, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""
    list_display = ['name', 'slug', 'created_at', 'post_count']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model"""
    list_display = ['name', 'slug', 'created_at', 'post_count']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Posts'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""
    list_display = ['user', 'role', 'created_at', 'has_avatar']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Profile Details', {
            'fields': ('bio', 'avatar', 'website', 'twitter')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_avatar(self, obj):
        if obj.avatar:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_avatar.short_description = 'Avatar'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model"""
    list_display = [
        'title', 'author', 'status', 'category', 'published_at',
        'view_count', 'featured', 'comment_count'
    ]
    list_filter = [
        'status', 'featured', 'category', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'created_at', 'updated_at', 'view_count', 'get_reading_time'
    ]
    date_hierarchy = 'published_at'
    filter_horizontal = ['tags']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Organization', {
            'fields': ('category', 'tags', 'status', 'featured')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps & Stats', {
            'fields': (
                'created_at', 'updated_at', 'published_at',
                'view_count', 'get_reading_time'
            ),
            'classes': ('collapse',)
        }),
    )

    def comment_count(self, obj):
        return obj.get_comment_count()
    comment_count.short_description = 'Comments'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new post
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model"""
    list_display = ['post', 'author', 'active', 'created_at', 'is_reply_to']
    list_filter = ['active', 'created_at', 'post']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['make_active', 'make_inactive']

    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'author', 'content', 'parent')
        }),
        ('Status', {
            'fields': ('active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_reply_to(self, obj):
        if obj.parent:
            return f"Reply to: {obj.parent.author.username}"
        return "Original comment"
    is_reply_to.short_description = 'Type'

    def make_active(self, request, queryset):
        queryset.update(active=True)
    make_active.short_description = "Mark selected comments as active"

    def make_inactive(self, request, queryset):
        queryset.update(active=False)
    make_inactive.short_description = "Mark selected comments as inactive"


# Customize admin site header and title
admin.site.site_header = "Blog Administration"
admin.site.site_title = "Blog Admin Portal"
admin.site.index_title = "Welcome to Blog Administration"
