from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import auth
from django.contrib import messages
from .models import Comment, ContactMessage, CustomUser, Post
from .forms import CommentForm, ContactForm
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.http import HttpRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext as _
from .models import ContactMessage
from .utils import generate_otp, send_otp_email
from django.utils import timezone
from django.core.mail import send_mail
from django.utils import timezone

import pytz
import re
import json
import datetime


CustomUser = get_user_model()


# Create your views here.
def SignUp(request):
    """
    User registration view.
    """
    if request.method == "POST":
        # Retrieve form inputs
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email_input = request.POST.get("email_input")
        phone_number = request.POST.get("phone_number")
        status = request.POST.get("status")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Perform validations
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif not Password_Security(password):
            messages.error(request, "Password is not strong enough")
        elif not is_valid_email(email_input):
            messages.error(request, "Invalid email address")
        elif not is_valid_phone_number(phone_number):
            messages.error(request, "Invalid phone number")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username Taken")
        else:
            # Create user if all validations pass
            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email_input,
                password=password,
                is_active=False,
            )
            if user is not None:
                # Set status attribute
                user.status = status
                user.save()

                # Generate OTP only for new registrations
                otp = generate_otp()
                # Send OTP via email
                send_otp_email(user.email, otp)
                # Save OTP in session for verification
                request.session['otp'] = otp
                request.session['user_id'] = user.id
                # Save phone number to user model
                user.phone_number = phone_number
                user.save()
                messages.success(request, "An OTP has been sent to your email. Please enter it to activate your account.")
                return redirect("VerifyOTP")
            else:
                messages.error(request, "Failed try again.")

    return render(request, "SignUp.html")


def VerifyOTP(request):
    """
    OTP verification view.
    """
    resent = False

    if request.method == "POST":
        if 'resend_otp' in request.POST:
            # User clicked on the resend OTP button
            new_otp = generate_otp()
            request.session['otp'] = new_otp
            request.session['otp_sent_time'] = timezone.now().isoformat()
            # Send the new OTP via email
            user_id = request.session.get("user_id")
            user = CustomUser.objects.get(pk=user_id)
            send_otp_email(user.email, new_otp)
            resent = True
            messages.info(request, "A new OTP has been sent to your email.")
            return redirect("VerifyOTP")

        # User submitted the OTP verification form
        otp_entered = request.POST.get("otp")
        otp_sent = request.session.get("otp")
        user_id = request.session.get("user_id")

        if otp_entered == otp_sent:
            # Activate user account
            user = CustomUser.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been successfully activated.")
            return redirect("SignIn")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "verify_otp.html", {'resent': resent})


def is_valid_email(email):
    """
    Email validation function.
    """
    return re.match(r'^[\w\.-]+@gmail\.com$', email)


def is_valid_phone_number(phone_number):
    """Phone Number validation function.
    """
    return re.match(r'^\+[0-9]{10}$', phone_number)


def Password_Security(password):
    """
    Password security validation function.
    """
    if len(password) < 8:
        return False

    if not re.search(r"[A-Za-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True


@login_required(login_url="SignIn")
def LogOut(request):
    """
    User logout function.
    """
    auth.logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("SignIn")


def SignIn(request):
    """
    User login function.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("threads")
        else:
            messages.error(request, "Invalid Credentials")
            return render(request, "SignIn.html", {"username": username})
    else:
        return render(request, "SignIn.html")


def account(request, pk):
    """
    account Details function.
    """
    user_account = get_object_or_404(CustomUser, pk=pk)
    return render(request, "account.html", {"user_account": user_account})


@login_required(login_url="SignIn")
def settings(request):
    """
    User profile settings function.
    """
    user_account = request.user

    if request.method == "POST":
        username = request.POST.get("username", "")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        email = request.POST.get("email", "")
        status = request.POST.get("status", "")

        user_account.username = username
        user_account.first_name = first_name
        user_account.last_name = last_name
        user_account.email = email
        user_account.status = status

        if "account_picture" in request.FILES:
            account_picture = request.FILES["account_picture"]
            user_account.account_picture = account_picture

        user_account.save()

        messages.success(request, "Account updated")

        return redirect("account", user_account.pk)

    return render(request, "settings.html", {"user_account": user_account})


def threads(request):
    """
    List of all blogs.
    """
    category_filter = request.GET.get('category')
    if category_filter:
        posts = Post.objects.filter(category=category_filter)
    else:
        posts = Post.objects.all()

    # Paginate the queryset
    paginator = Paginator(posts, 3)  # Display 3 posts per page
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    categories = set([post.get_category_display() for post in posts])
    category_choices = Post.CATEGORY_CHOICES
    return render(request, 'threads.html', {'posts': posts,
                                            'choices': categories,
                                            'category_choices':
                                                category_choices})


def summary(request, pk):
    """
    Preview of a post.
    """
    referer = request.META.get('HTTP_REFERER')
    if referer and 'summary' in referer:
        post = get_object_or_404(Post, pk=pk)
        return render(request, 'summary.html', {'post': post})

    post = get_object_or_404(Post, pk=pk)
    post.views += 1
    post.save()

    # Convert the created_at time to Kenyan timezone
    nairobi_tz = pytz.timezone('Africa/Nairobi')
    post.created_at = timezone.localtime(post.created_at, timezone=nairobi_tz)

    return render(request, 'summary.html', {'post': post})


@login_required(login_url='SignIn')
def created(request):
    """
    Create a new Blog.
    """
    # Retrieve category choices
    category_choices = Post.CATEGORY_CHOICES

    if request.method == 'POST':
        author = request.user
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        # Get selected categories
        categories = request.POST.getlist('category')

        # Check if all fields are provided
        if title and content and categories:  
            # Create a separate post for each selected category
            for category in categories:
                post = Post.objects.create(author=author, title=title,
                                           content=content, category=category)
                messages.success(request, _('Blog created!'))

            # Convert the created_at time to Eastern Africa Time (EAT)
            eat_tz = pytz.timezone('Africa/Nairobi')
            post.created_at = timezone.localtime(post.created_at,
                                                 timezone=eat_tz)

            # Redirect to the last created post
            return redirect('summary', pk=post.pk)
        else:
            error_messages = []
            if not title:
                error_messages.append(_('Title is required.'))
            if not content:
                error_messages.append(_('Content is required.'))
            if not categories:
                error_messages.append(_('Category is required.'))
            if error_messages:
                error_message = ', '.join(error_messages)
                messages.error(request, error_message)
            else:
                messages.error(request, _('Please provide title, content, and category.'))

    return render(request, 'create.html', {'category_choices': category_choices})


@login_required(login_url='SignIn')
def updated(request, pk):
    """
    Blog update view.
    """
    post = get_object_or_404(Post, pk=pk)

    # Checks if the current user is the author of the post
    if request.user != post.author:
        messages.error(
            request, 'Oops! You do not have the permission to update.')
        return redirect('summary', pk=pk)

    # Retrieve category choices
    category_choices = Post.CATEGORY_CHOICES

    if request.method == 'POST':
        # Retrieve form data
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        category = request.POST.get('category', '')

        # Check if all fields are provided
        if title and content and category:
            post.title = title
            post.content = content
            post.category = category
            post.save()
            messages.success(request, 'Blog updated!')
            return redirect('summary', pk=post.pk)
        else:
            messages.error(
                request, 'Please provide title, content, and select a category.')

    return render(request, 'create.html', {'post': post, 'category_choices': category_choices})


@login_required(login_url='SignIn')
def delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(
            request, 'Oops! You do not have the permission to delete.')
        return redirect('summary', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog deleted!')
        return redirect('threads')

    return render(request, 'delete.html', {'post': post})


# Comments view
@login_required(login_url='SignIn')
def Commented(request, pk):
    """
    Comments on a post.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.created_at = datetime.now()
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('summary', pk=post.pk)
        else:
            messages.error(request, 'Comment cannot be empty.')
    else:
        form = CommentForm()
    return render(request, 'comments.html', {'post': post, 'form': form})


@login_required(login_url='SignIn')
def delete_comment(request, comment_id):
    """
    Delete a comment.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author:
        comment.delete()
        messages.success(request, 'Comment deleted!')
    else:
        messages.error(request,
                       "You don't have permission to delete this comment.")
    return redirect('summary', pk=comment.post.pk)


@login_required(login_url='SignIn')
def like_post(request, pk):
    """
    Like a post.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.user not in post.likes.all():
        post.likes.add(request.user)
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='SignIn')
def dislike_post(request, pk):
    """
    Dislike a post.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.user not in post.dislikes.all():
        post.dislikes.add(request.user)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='SignIn')
def like_comment(request, pk):
    """
    Like a comment.
    """
    comment = get_object_or_404(Comment, pk=pk)
    if request.user not in comment.likes.all():
        comment.likes.add(request.user)
        if request.user in comment.dislikes.all():
            comment.dislikes.remove(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='SignIn')
def dislike_comment(request, pk):
    """
    Dislike a comment.
    """
    comment = get_object_or_404(Comment, pk=pk)
    if request.user not in comment.dislikes.all():
        comment.dislikes.add(request.user)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def about_us(request):
    """
    Bried Details about the website
    """
    return render(request, 'about.html')


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {'form': ContactForm(),
                                                    'success_message': True})
        else:
            return render(request, 'contact.html', {'form': form,
                                                    'error_message': True})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


"""def contact_us(request, email_host_user=settings.EMAIL_HOST_USER):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send email notification to user
            send_mail(
                'Message Received',
                f'Dear {name},\n\nThank you for contacting us. We have received your message and will get back to you soon.\n\nBest regards,\nThe Support Team',
                settings.EMAIL_HOST_USER,  # Sender's email address from settings
                [email],  # User's email address
                fail_silently=False,
            )

            # Send email notification to admin
            send_mail(
                'New Contact Form Submission',
                f'Name: {name}\nEmail: {email}\nMessage: {message}',
                settings.EMAIL_HOST_USER,  # Sender's email address from settings
                ['jnabango@gmail.com'],  # Admin's email address
                fail_silently=False,
            )

            # Render a success message
            success_message = "Your message has been sent successfully. We'll get back to you soon."
            return render(request, 'contact.html', {'form': ContactForm(), 'success_message': success_message})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
"""
