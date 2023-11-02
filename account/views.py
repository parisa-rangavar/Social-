import os

from django.shortcuts import render ,redirect ,get_object_or_404 ,get_list_or_404
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm, EditUserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relations, Profile


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name ='account/register.html'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    def get(self,request):
        form = self.form_class()
        return render(request,self.template_name,{'form':form})
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'],cd['email'],cd['password1'])
            messages.success(request,'You registered successfully','success')
            return redirect('home:home')
        return render(request,self.template_name, {'form': form})


class UserLoginview(View):
    form_class = UserLoginForm
    template_name= 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self,request):
        form = self.form_class
        return render(request,self.template_name,{'form':form})
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'],password = cd['password'])
            if user is not None:
                login(request,user)
                messages.success(request,'you logged in successfully', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request,'username or password is wrong','warning')
        return render(request, self.template_name ,{'form':form})

class UserLogoutView(LoginRequiredMixin,View):
    def get(self,request):
        logout(request)
        messages.success(request,'you logged out successfully','success')
        return redirect ('home:home')


class UserProfileView(LoginRequiredMixin, View):
    def get(self,request,user_id):
        is_following=False
        user = get_object_or_404(User, pk=user_id)
        # posts = Post.objects.filter(user=user)
        # image = user.profile.image.url
        posts = user.posts.all()
        relation=Relations.objects.filter(from_users=request.user, to_user=user)
        if relation.exists():
            is_following = True
        # return render(request,'account/profile.html',{'user':user,'image':image ,'posts':posts, 'is_following':is_following} )
        return render(request, 'account/profile.html', {'user': user, 'posts': posts, 'is_following': is_following} )


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    success_url = reverse_lazy('account:password_reset_done')
    email_template_name = 'account/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):
    def get(self,request,user_id):
        user = User.objects.get(id=user_id)
        relation = Relations.objects.filter(from_users=request.user, to_user=user)
        if relation.exists():
            messages.error(request,'you are already folling this user', 'danger')
        else:
            Relations(from_users=request.user, to_user=user).save()
            messages.success(request,'you followed this user', 'success')
        return redirect('account:user_profile', user.id)


class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relations.objects.filter(from_users=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request,'you unfollowed this user','success')
        else:
            messages.error(request,'you are not following this user','danger')
        return redirect('account:user_profile', user_id)


class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserForm
    # def get(self, request):
    #     # form = self.form_class(instance=request.user.profile, initial={'email':request.user.email,'image': request.user.profile.image})
    #     form = self.form_class(instance=request.user.profile, initial={'email':request.user.email})
    #     return render(request,'account/edit_profile.html', {'form':form})

    def get(self, request):
        user = request.user
        profile = user.profile
        initial_data = {
            'email': user.email,
            'age': profile.age,
            'bio': profile.bio,
        }
        form = self.form_class(instance=profile, initial=initial_data)
        return render(request, 'account/edit_profile.html', {'form': form})


    # def post(self, request, **kwargs):
    #     form = self.form_class(request.POST, request.FILES, instance=request.user.profile)
    #     print("=============================")
    #     print(f'form valid:  {form.is_valid()}')
    #     if form.is_valid():
    #         profile = form.save(commit=False)
    #         request.user.email = form.cleaned_data.get('email')
    #         request.user.save()
    #         # profile = Profile.objects.get(user=request.user)
    #
    #         image_clean = form.cleaned_data.get('image')
    #         # image_clean = request.FILES['image']
    #
    #         profile.image = image_clean
    #         profile.save()
    #         print('----------------------------')
    #         print(f'profile: {profile}')
    #         print(f'image: {image_clean}')
    #         print('----------------------------')
    #         # profile.save()
    #         # request.user.save()
    #         # profile.save()
    #         messages.success(request,'profile edited successfully','success')
    #     return redirect('account:user_profile', request.user.id)
    def post(self, request):
        user = request.user
        profile = user.profile

        # Erstelle das Formular mit den gesendeten Daten
        form = self.form_class(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            # Speichere die Daten im Modell
            user.email = form.cleaned_data.get('email')
            profile.age = form.cleaned_data.get('age')
            profile.bio = form.cleaned_data.get('bio')
            print(f'{form.cleaned_data}')
            print(f'{request.FILES}')
            if 'image' in request.FILES:
                profile.image = request.FILES['image']


            user.save()
            profile.save()
            print('++++++++++')

            return redirect('account:user_profile', user.id)  # Weiterleitung zur Profilansicht
        else:
            # Das Formular war ungültig, zeige es erneut an
            return render(request, 'account/edit_profile.html', {'form': form})




