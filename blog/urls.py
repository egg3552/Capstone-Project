from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'blog'

urlpatterns = [
    # === AUTHENTICATION URLS ===
    # Custom user registration with role selection
    path('register/', views.register_view, name='register'),

    # User profile management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Django built-in auth views with custom templates
    # LoginView handles GET (show form) and POST (process login)
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # === PASSWORD RESET FLOW ===
    # Step 1: User requests password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'),
         name='password_reset'),
    # Step 2: Confirmation that email was sent
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    # Step 3: User clicks link in email with encoded user ID and token
    # <uidb64> = base64 encoded user ID, <token> = password reset token
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    # Step 4: Password successfully reset confirmation
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    # === BLOG URLS ===
    # Landing page - main entry point
    path('', views.landing_page, name='landing_page'),
    # Blog list page with pagination and filtering
    path('blog/', views.PostListView.as_view(), name='post_list'),

    # Post CRUD operations
    # Create new post (requires author/admin permissions)
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    # View individual post by slug (SEO-friendly URLs)
    # <slug:slug> captures URL-friendly post identifier
    path('post/<slug:slug>/', views.PostDetailView.as_view(),
         name='post_detail'),
    # Edit existing post (author or admin only)
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(),
         name='post_edit'),
    # Delete post with confirmation (author or admin only)
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(),
         name='post_delete'),

    # === COMMENT SYSTEM ===
    # Add comment to specific post (requires login)
    path('post/<slug:slug>/comment/', views.add_comment_view,
         name='add_comment'),
    # Delete comment by ID (author or admin only)
    # <int:comment_id> captures numeric comment identifier
    path('comment/<int:comment_id>/delete/', views.delete_comment_view,
         name='delete_comment'),

    # === CONTENT ORGANIZATION ===
    # Filter posts by category using slug
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(),
         name='category_detail'),
    # Filter posts by tag using slug
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),

    # === STATIC PAGES ===
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # === ADVANCED FEATURES ===
    # Newsletter subscription (AJAX endpoint)
    path('newsletter/subscribe/', views.newsletter_subscribe,
         name='newsletter_subscribe'),

    # Post reactions system (AJAX endpoint for like/love/etc)
    path('post/<slug:slug>/react/', views.add_reaction, name='add_reaction'),

    # Analytics dashboard (author/admin only)
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    # Advanced search with multiple filters
    path('search/', views.advanced_search, name='advanced_search'),

    # Reading progress tracking (AJAX endpoint)
    # Updates user's reading progress percentage for a post
    path('post/<slug:slug>/progress/', views.update_reading_progress,
         name='update_reading_progress'),

    # === LEGAL PAGES ===
    path('terms/', views.terms_of_service_view, name='terms'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
]
