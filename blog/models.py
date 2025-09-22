from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from PIL import Image


class Category(models.Model):
    """
    Model for blog post categories.
    Allows organizing posts into different topics/categories.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """
    Model for blog post tags.
    Allows more granular organization and filtering of posts.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})


class UserProfile(models.Model):
    """
    Extended user profile with additional information.
    Links to Django's built-in User model.
    """
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('author', 'Author'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='reader'
    )
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize avatar image to improve page load performance
        if self.avatar:
            img = Image.open(self.avatar.path)
            # Only resize if image is larger than 300x300 pixels
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)  # Maintain aspect ratio
                img.save(self.avatar.path)

    def can_create_posts(self):
        """Check if user can create blog posts"""
        return self.role in ['author', 'admin']

    def can_moderate(self):
        """Check if user can moderate content"""
        return self.role == 'admin'


class Post(models.Model):
    """
    Main blog post model with full content management features.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    content = RichTextUploadingField()
    excerpt = models.TextField(
        max_length=500, blank=True,
        help_text="Short description of the post"
    )
    featured_image = models.ImageField(
        upload_to='posts/', blank=True, null=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft'
    )
    
    # SEO and metadata
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement metrics
    view_count = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)

    class Meta:
        # Most recent published posts first
        ordering = ['-published_at', '-created_at']
        indexes = [
            # Optimize queries for published posts by date
            models.Index(fields=['status', 'published_at']),
            # Optimize author's post queries
            models.Index(fields=['author', 'status']),
            # Optimize category-based filtering
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        # Set published_at timestamp when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def is_published(self):
        return self.status == 'published' and self.published_at

    def get_comment_count(self):
        return self.comments.filter(active=True).count()

    def get_reading_time(self):
        """Estimate reading time based on content length"""
        words_per_minute = 200  # Average adult reading speed
        word_count = len(self.content.split())
        reading_time = word_count / words_per_minute
        return max(1, round(reading_time))  # Minimum 1 minute


class Comment(models.Model):
    """
    Comment system for blog posts with moderation support.
    """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies'  # Enables hierarchical comment threading
    )

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'active', 'created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

    def get_replies(self):
        return self.replies.filter(active=True)

    def is_reply(self):
        return self.parent is not None


class NewsletterSubscription(models.Model):
    """
    Newsletter subscription model for email marketing.
    """
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        
    def __str__(self):
        return self.email


class PostReaction(models.Model):
    """
    Post reaction system (likes, loves, etc.).
    """
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('laugh', 'Laugh'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='reactions'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reactions'
    )
    reaction_type = models.CharField(
        max_length=10, choices=REACTION_CHOICES, default='like'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')  # One reaction per user per post
        ordering = ['-created_at']
        indexes = [
            # Optimize reaction count queries by type
            models.Index(fields=['post', 'reaction_type']),
        ]
    
    def __str__(self):
        return f'{self.user.username} {self.reaction_type}d {self.post.title}'


class ReadingProgress(models.Model):
    """
    Track user reading progress on posts.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    progress_percentage = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # One progress record per user per post
        unique_together = ('user', 'post')
        ordering = ['-last_read_at']
    
    def __str__(self):
        return (f'{self.user.username} - {self.post.title} '
                f'({self.progress_percentage}%)')
