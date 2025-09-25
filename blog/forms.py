from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    UserProfile, Comment, Post, NewsletterSubscription, PostReaction
)


class CustomUserCreationForm(UserCreationForm):
    """
    Extended user registration form with additional fields.
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial='reader'
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",
                  "password1", "password2", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap CSS classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # Special styling for select dropdown
            if field_name == 'role':
                field.widget.attrs['class'] = 'form-select'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            # Create or update user profile with selected role
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data["role"]
            profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.
    """

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'website', 'twitter']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Add help text
        self.fields['bio'].help_text = 'Tell us about yourself'
        self.fields['twitter'].help_text = 'Twitter username (without @)'


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user account information.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to blog posts.
    """

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                    'placeholder': 'Add your comment...'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = 'Comment'


class PostForm(forms.ModelForm):
    """
    Form for creating and editing blog posts.
    """

    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'category', 'tags', 'status', 'featured', 'meta_description',
            'meta_keywords'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(
                attrs={'rows': 15, 'class': 'form-control'}
            ),
            'excerpt': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'featured': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'meta_description': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'meta_keywords': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set form help text
        self.fields['title'].help_text = 'Enter a descriptive title'
        self.fields['slug'].help_text = 'URL-friendly version of the title'
        self.fields['excerpt'].help_text = 'Short description for previews'
        self.fields['meta_description'].help_text = (
            'SEO description (max 160 characters)'
        )
        self.fields['meta_keywords'].help_text = (
            'SEO keywords, separated by commas'
        )

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        # Check if slug is unique (excluding current post if editing)
        queryset = Post.objects.filter(slug=slug)
        # Allow same slug when editing existing post
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                'A post with this slug already exists.'
            )
        return slug


class PostSearchForm(forms.Form):
    """
    Form for searching blog posts.
    """
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.all()


class NewsletterSubscriptionForm(forms.ModelForm):
    """
    Form for newsletter subscription.
    """
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email for updates...'
            })
        }


class PostReactionForm(forms.ModelForm):
    """
    Form for post reactions.
    """
    class Meta:
        model = PostReaction
        fields = ['reaction_type']
        widgets = {
            'reaction_type': forms.HiddenInput()
        }


class AdvancedSearchForm(forms.Form):
    """
    Advanced search form with additional filters.
    """
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts, content, and authors...'
        })
    )
    author = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Authors",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tag = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically load categories, tags, and authors for dropdown filters
        from .models import Category, Tag
        from django.contrib.auth.models import User
        
        self.fields['category'].queryset = Category.objects.all()
        self.fields['tag'].queryset = Tag.objects.all()
        self.fields['author'].queryset = User.objects.filter(
            posts__isnull=False
        ).distinct().order_by('username')
