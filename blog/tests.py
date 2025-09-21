from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment, Category, Tag
from .forms import CustomUserCreationForm, PostForm, PostSearchForm


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test UserProfile is created automatically with User."""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertEqual(self.user.userprofile.role, 'reader')
    
    def test_user_profile_str(self):
        """Test UserProfile string representation."""
        expected = f"{self.user.username} - {self.user.userprofile.role}"
        self.assertEqual(str(self.user.userprofile), expected)


class CategoryModelTest(TestCase):
    """Test cases for Category model."""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Technology',
            description='Tech related posts'
        )
    
    def test_category_creation(self):
        """Test Category model creation."""
        self.assertEqual(self.category.name, 'Technology')
        self.assertEqual(self.category.slug, 'technology')
        self.assertTrue(self.category.description)
    
    def test_category_str(self):
        """Test Category string representation."""
        self.assertEqual(str(self.category), 'Technology')


class TagModelTest(TestCase):
    """Test cases for Tag model."""
    
    def setUp(self):
        self.tag = Tag.objects.create(name='Django')
    
    def test_tag_creation(self):
        """Test Tag model creation."""
        self.assertEqual(self.tag.name, 'Django')
        self.assertEqual(self.tag.slug, 'django')
    
    def test_tag_str(self):
        """Test Tag string representation."""
        self.assertEqual(str(self.tag), 'Django')


class PostModelTest(TestCase):
    """Test cases for Post model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            description='Tech posts'
        )
        self.tag = Tag.objects.create(name='Django')
        self.post = Post.objects.create(
            title='Test Post',
            content='This is test content.',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.post.tags.add(self.tag)
    
    def test_post_creation(self):
        """Test Post model creation."""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.status, 'published')
        self.assertTrue(self.post.slug)
    
    def test_post_str(self):
        """Test Post string representation."""
        self.assertEqual(str(self.post), 'Test Post')
    
    def test_post_absolute_url(self):
        """Test Post get_absolute_url method."""
        expected_url = reverse('blog:post_detail',
                               kwargs={'slug': self.post.slug})
        self.assertEqual(self.post.get_absolute_url(), expected_url)


class CommentModelTest(TestCase):
    """Test cases for Comment model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='commenterpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            description='Tech posts'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content.',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment content.'
        )
    
    def test_comment_creation(self):
        """Test Comment model creation."""
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, 'Test comment content.')
        self.assertTrue(self.comment.created_at)
    
    def test_comment_str(self):
        """Test Comment string representation."""
        expected = f"Comment by {self.user.username} on {self.post.title}"
        self.assertEqual(str(self.comment), expected)


class CustomUserCreationFormTest(TestCase):
    """Test cases for CustomUserCreationForm."""
    
    def test_valid_form(self):
        """Test CustomUserCreationForm with valid data."""
        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'reader'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords."""
        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
            'role': 'reader'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())


class PostFormTest(TestCase):
    """Test cases for PostForm."""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Technology',
            description='Tech posts'
        )
    
    def test_valid_post_form(self):
        """Test PostForm with valid data."""
        form_data = {
            'title': 'Test Post',
            'slug': 'test-post',
            'content': 'This is test content for the post.',
            'excerpt': 'Test excerpt',
            'category': self.category.id,
            'status': 'published',
            'featured': False,
            'meta_description': 'Test meta description',
            'meta_keywords': 'test, keywords'
        }
        form = PostForm(data=form_data)
        if not form.is_valid():
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid())
    
    def test_empty_title(self):
        """Test PostForm with empty title."""
        form_data = {
            'title': '',
            'content': 'This is test content.',
            'category': self.category.id,
            'status': 'published'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())


class ViewsTest(TestCase):
    """Test cases for blog views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.userprofile.role = 'author'
        self.user.userprofile.save()
        
        self.category = Category.objects.create(
            name='Technology',
            description='Tech posts'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content.',
            author=self.user,
            category=self.category,
            status='published'
        )
    
    def test_post_list_view(self):
        """Test post list view."""
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
    
    def test_post_detail_view(self):
        """Test post detail view."""
        response = self.client.get(
            reverse('blog:post_detail', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
    
    def test_register_view(self):
        """Test user registration view."""
        response = self.client.get(reverse('blog:register'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view(self):
        """Test login view."""
        response = self.client.get(reverse('blog:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_post_create_requires_login(self):
        """Test post creation requires authentication."""
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_post_create_authenticated(self):
        """Test post creation with authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 200)


class URLPatternsTest(TestCase):
    """Test cases for URL patterns."""
    
    def test_post_list_url(self):
        """Test post list URL resolves correctly."""
        url = reverse('blog:post_list')
        self.assertEqual(url, '/')
    
    def test_register_url(self):
        """Test register URL resolves correctly."""
        url = reverse('blog:register')
        self.assertEqual(url, '/register/')
    
    def test_login_url(self):
        """Test login URL resolves correctly."""
        url = reverse('blog:login')
        self.assertEqual(url, '/login/')
    
    def test_post_create_url(self):
        """Test post create URL resolves correctly."""
        url = reverse('blog:post_create')
        self.assertEqual(url, '/post/create/')


class SearchFunctionalityTest(TestCase):
    """Test cases for search functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            description='Tech posts'
        )
        self.post1 = Post.objects.create(
            title='Django Tutorial',
            content='Learn Django web framework.',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.post2 = Post.objects.create(
            title='Python Basics for Beginners',
            content='Introduction to Python programming.',
            author=self.user,
            category=self.category,
            status='published'
        )
    
    def test_search_form(self):
        """Test search form functionality."""
        form_data = {'query': 'Django'}
        form = PostSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_search(self):
        """Test search form with empty query."""
        form_data = {'query': ''}
        form = PostSearchForm(data=form_data)
        self.assertTrue(form.is_valid())  # Empty search should be valid
