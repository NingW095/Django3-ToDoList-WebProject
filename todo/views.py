from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import TodoForm
from .models import Todo
# Create your views here.

def home(request):
    return render(request, 'todo/home.html')


def user_signup(request):

    if request.method == "GET":
        return render(request, 'todo/user_signup.html', {'form': UserCreationForm()})
    else:
        #Create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:   # handel same name user
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request, 'todo/user_signup.html',
                              {'form': UserCreationForm(), 'error': 'That username has already been taken, please choose a new user name!'})
        else:
            # password didn't match
            return render(request, 'todo/user_signup.html',
                          {'form': UserCreationForm(), 'error': 'Passwords did not match!'})




def user_login(request):
    if request.method == "GET":
        return render(request, 'todo/user_login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/user_login.html', {'form': AuthenticationForm(), 'error': 'Username and password did not match'})
        else:
            login(request, user)
            return redirect('current_todos')


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo/create_todo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)    # do not save to the data base yet
            new_todo.user = request.user
            new_todo.save()    #save to the data base
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/create_todo.html', {'form': TodoForm()})


@login_required
def current_todos(request):
    all_todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo/current.html', {'all_todos': all_todos})

@login_required
def completed_todos(request):
    all_completed_todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo/completed.html', {'all_completed_todos': all_completed_todos})

@login_required
def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)  # user can only check todos belong to himself by setting user=request.user
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'error': 'Bad data passed in'})


@login_required
def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('current_todos')

@login_required
def delete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('current_todos')