from django.shortcuts import render,redirect
from .models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .forms import ArticleForm
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.views.decorators.http import require_POST

def categoryview(request, cat_name):
    category = get_object_or_404(Category, name=cat_name)
    category_articles = Article.objects.filter(category=category)
    return render(request, 'categories.html', {
        'category': category,
        'category_articles': category_articles,
    })

def Homepage(request):
    articles = Article.objects.all()
    return render(request, 'index.html', {'articles':articles})


@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        category = Category.objects.get(id=category_id)
        Article.objects.create(
            title=title,
            content=content,
            category=category,
            author=request.user,
            image=image
        )
        return redirect('homepage')
    categories = Category.objects.all()
    return render(request, 'create.html', {'categories': categories})


def update(request, id):
    teacher = get_object_or_404(Article, id=id)
    if request.method == 'POST':
      Article.title = request.POST['title']
      Article.content = request.POST['content']
      Article.author= request.POST['author']
      Article.category = request.POST['category']
      return redirect('/')
    return render(request, 'edit_page.html', {'teacher': teacher})

def post_delete(request, id):
    post = get_object_or_404(Article, id=id)
    if request.method == 'POST':
        post.delete()
        return redirect('homepage')
    return render(request, 'delete.html', {'post': post})





def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists.")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists.")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('homepage') 
        else:
            messages.error(request, "Passwords do not match.")
            return redirect('homepage')

    return render(request, "sign_up.html")
def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect("homepage")
        else:
            messages.info(request,'Username or Password is incorrect')
            return redirect("signin")
            
    return render(request,"login_page.html")

@require_POST
def log_out(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('homepage')



def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    is_author = request.user.is_authenticated and request.user == article.author
    comments = article.comments.all().order_by('-date_posted')

    if request.method == "POST":
        if is_author and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.POST.get('delete'):
                article.delete()
                return JsonResponse({'status': 'deleted'})

            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})
        elif request.user.is_authenticated:
            comment_content = request.POST.get('comment', '').strip()
            parent_id = request.POST.get('parent_id')  

            if comment_content:
                parent_comment = None
                if parent_id:
                    try:
                        parent_comment = Comment.objects.get(id=parent_id, article=article)
                    except Comment.DoesNotExist:
                        parent_comment = None

                if parent_comment and request.user == article.author:
                    Comment.objects.create(
                        article=article,
                        author=request.user,
                        content=comment_content,
                        parent=parent_comment
                    )
                elif not parent_comment:
                    Comment.objects.create(
                        article=article,
                        author=request.user,
                        content=comment_content
                    )
                return redirect('article_detail', pk=pk)

    else:
        form = ArticleForm(instance=article) if is_author else None

    return render(request, 'article_detail.html', {
        'article': article,
        'form': form,
        'is_author': is_author,
        'comments': comments
    })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        return HttpResponseForbidden("You cannot delete this comment.")

    article_id = comment.article.pk
    comment.delete()
    return redirect('article_detail', pk=article_id)


@login_required
def like_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    liked = False

    if request.user in article.likes.all():
        article.likes.remove(request.user)
    else:
        article.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'total_likes': article.likes.count()
    })



def contact_us(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST.get('subject', '')
        message = request.POST['message']
        

        messages.success(request, "Message sent successfully!")
        return redirect('contact')  

    return render(request, "contact.html")