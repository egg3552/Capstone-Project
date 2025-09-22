from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy

from .models import Post, Comment, Category, Tag
from .forms import (
    CustomUserCreationForm, UserUpdateForm, UserProfileForm,
    CommentForm, PostForm, PostSearchForm
)


# Authentication Views
def register_view(request):
    """
    User registration view with role selection.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')

            # Automatically log in the user
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('blog:post_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    """
    User profile view showing user information and posts.
    """
    user_posts = Post.objects.filter(
        author=request.user
    ).order_by('-created_at')
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_posts': page_obj,
        'total_posts': user_posts.count(),
    }
    # Temporarily use post_list template to test
    return render(request, 'blog/post_list.html', context)


@login_required
def edit_profile_view(request):
    """
    Edit user profile view.
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES,
            instance=request.user.userprofile,
            user=request.user
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('blog:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(
            instance=request.user.userprofile,
            user=request.user
        )

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'blog/edit_profile.html', context)


# Blog Views
class PostListView(ListView):
    """
    Main blog post listing view with search and filtering.
    """
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(status='published').select_related(
            'author', 'category').prefetch_related('tags')

        # Search functionality
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )

        # Category filtering
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Tag filtering
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        return queryset.order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PostSearchForm(self.request.GET)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['featured_posts'] = Post.objects.filter(
            status='published', featured=True)[:3]
        return context


class PostDetailView(DetailView):
    """
    Individual blog post view with comments.
    """
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related(
            'author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Increment view count
        Post.objects.filter(pk=post.pk).update(view_count=post.view_count + 1)

        # Get comments
        comments = Comment.objects.filter(
            post=post, active=True, parent=None
        ).select_related('author').order_by('created_at')

        context['comments'] = comments
        context['comment_form'] = CommentForm()
        context['related_posts'] = Post.objects.filter(
            status='published', category=post.category
        ).exclude(pk=post.pk)[:3]

        return context


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    """
    Create new blog post view (authors and admins only).
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.userprofile.can_create_posts():
            messages.error(
                request, 'You do not have permission to create posts.'
            )
            return redirect('blog:post_list')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    """
    Update blog post view (author or admin only).
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if (request.user != post.author and
                not request.user.userprofile.can_moderate()):
            messages.error(request, 'You can only edit your own posts.')
            return redirect('blog:post_detail', slug=post.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):
    """
    Delete blog post view (author or admin only).
    """
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if (request.user != post.author and
                not request.user.userprofile.can_moderate()):
            messages.error(request, 'You can only delete your own posts.')
            return redirect('blog:post_detail', slug=post.slug)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Comment Views
@login_required
def add_comment_view(request, slug):
    """
    Add comment to a blog post.
    """
    post = get_object_or_404(Post, slug=slug, status='published')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            # Handle reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment

            comment.save()
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')

    return redirect('blog:post_detail', slug=slug)


@login_required
def delete_comment_view(request, comment_id):
    """
    Delete a comment (author or admin only).
    """
    comment = get_object_or_404(Comment, id=comment_id)

    if (request.user == comment.author or
            request.user.userprofile.can_moderate()):
        post_slug = comment.post.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('blog:post_detail', slug=post_slug)
    else:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('blog:post_detail', slug=comment.post.slug)


# Category and Tag Views
class CategoryDetailView(ListView):
    """
    Posts by category view.
    """
    model = Post
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            category=self.category, status='published'
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagDetailView(ListView):
    """
    Posts by tag view.
    """
    model = Post
    template_name = 'blog/tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(
            tags=self.tag, status='published'
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


# Utility Views
def about_view(request):
    """
    About page view.
    """
    return render(request, 'blog/about.html')


def contact_view(request):
    """
    Contact page view.
    """
    return render(request, 'blog/contact.html')