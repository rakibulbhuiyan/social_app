from django.shortcuts import render,redirect,get_object_or_404
from django.views import generic
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile,Post,LikePost,FollowerCount
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from itertools import chain
import random
from django.views import View

# Create your views here.
@method_decorator(login_required(login_url='signin'), name='dispatch')
class IndexView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)
        user_following_list = []
        feed = []
        user_following = FollowerCount.objects.filter(follower=request.user.username)
        for users in user_following:
            user_following_list.append(users.user)
        for usernames in user_following_list:
            feed_lists = Post.objects.filter(user=usernames)
            feed.append(feed_lists)
        feed_list = list(chain(*feed))
        # user suggestion starts here......
        all_users = User.objects.all()
        user_following_all = []
        for user in user_following:
            user_list = User.objects.get(username=user.user)
            user_following_all.append(user_list)

        new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
        current_user = User.objects.filter(username=request.user.username)
        final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
        random.shuffle(final_suggestions_list)

        username_profile = []
        username_profile_list = []
        for users in final_suggestions_list:
            username_profile.append(users.id)
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        suggestions_username_profile_list = list(chain(*username_profile_list))

        context = {
            'user_profile': user_profile,
            'posts': feed_list,
            'suggestions_username_profile_list': suggestions_username_profile_list[:4],
        }
        return render(request, self.template_name, context)

@method_decorator(login_required(login_url='signin'), name='dispatch')
class SearchView(View):
    template_name = 'search.html'
    def get(self, request, *args, **kwargs):
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)
        return render(request, self.template_name, {'user_profile': user_profile})
    def post(self, request, *args, **kwargs):
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)

        if request.method == 'POST':
            username = request.POST['username']
            username_object = User.objects.filter(username__icontains=username)

            username_profile = []
            username_profile_list = []
            for users in username_object:
                username_profile.append(users.id)
            for ids in username_profile:
                profile_lists = Profile.objects.filter(id_user=ids)
                username_profile_list.append(profile_lists)    
            username_profile_list = list(chain(*username_profile_list))
        return render(request, self.template_name, {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@method_decorator(login_required(login_url='signin'), name='dispatch')
class FollowView(View):
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            follower = request.POST['follower']
            user = request.POST['user']

            if FollowerCount.objects.filter(follower=follower, user=user).first():
                delete_follower = FollowerCount.objects.get(follower=follower, user=user)
                delete_follower.delete()
            else:
                new_follower = FollowerCount.objects.create(follower=follower, user=user)
                new_follower.save()

        return redirect('/profile/' + user)

    def get(self, request, *args, **kwargs):
        return redirect('/')

@method_decorator(login_required(login_url='signin'), name='dispatch')
class ProfileView(View):
    template_name = 'profile.html'

    def get(self, request, pk, *args, **kwargs):
        user_object = get_object_or_404(User, username=pk)
        user_profile = Profile.objects.get(user=user_object)
        user_post = Post.objects.filter(user=pk)
        user_post_length = len(user_post)

        follower = request.user.username
        user = pk

        user_follower = len(FollowerCount.objects.filter(user=pk))
        user_following = len(FollowerCount.objects.filter(follower=pk))
        button_text = 'Unfollow' if FollowerCount.objects.filter(follower=follower, user=user).first() else 'Follow'

        context = {
            'user_object': user_object,
            'user_profile': user_profile,
            'user_post': user_post,
            'user_post_length': user_post_length,
            'button_text': button_text,
            'user_follower': user_follower,
            'user_following': user_following
        }
        return render(request, self.template_name, context)
    def post(self, request, pk, *args, **kwargs):
        if request.method == 'POST':
            follower = request.user.username
            user = pk

            if FollowerCount.objects.filter(follower=follower, user=user).first():
                delete_follower = FollowerCount.objects.get(follower=follower, user=user)
                delete_follower.delete()
            else:
                new_follower = FollowerCount.objects.create(follower=follower, user=user)
                new_follower.save()

        return redirect('profile', pk=pk)

@method_decorator(login_required(login_url='signin'),name='dispatch')
class LikePostView(View):
    def get(self,request,*args, **kwargs):
        username=request.user.username
        post_id=request.GET.get('post_id')
        post=Post.objects.get(id=post_id)

        like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
        if like_filter ==None:
            new_like=LikePost.objects.create(post_id=post_id, username=username)
            new_like.save()
            post.no_of_likes=post.no_of_likes+1
            post.save()
            
        else:
            like_filter.delete()
            post.no_of_likes=post.no_of_likes-1
            post.save()
        return redirect('/')
            

@method_decorator(login_required(login_url='signin'), name='dispatch')
class UploadView(View):
    def get(self, request, *args, **kwargs):
        return redirect('/')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            user = request.user.username
            image = request.FILES.get('image_upload')
            caption = request.POST['caption']
            
            new_post = Post.objects.create(user=user, image=image, caption=caption)
            new_post.save()
            
            return redirect('/')
        else:
            return redirect('/')

@method_decorator(login_required(login_url='signin'), name='dispatch')
class SettingsView(View):
    template_name = 'setting.html'  

    def get(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=request.user)
        return render(request, self.template_name, {'user_profile': user_profile})

    def post(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=request.user)
        
        image = user_profile.profileimg
        if request.FILES.get('image') is not None:
            image = request.FILES.get('image')

        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        return redirect('settings')

class SignupView(View):
    template_name='signup.html'
    def get(self,request,*args, **kwargs):
        return render(request, self.template_name)

    def post(self,request,*args, **kwargs):
        if request.method=='POST':
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['password']
            password2=request.POST['password2']
            if password==password2:
                if User.objects.filter(email=email).exists():
                    messages.info(request, "Email already taken")
                    return redirect('signup')
                elif User.objects.filter(username=username).exists():
                    messages.info(request, "Username already taken")
                    return redirect('signup')
                else:
                    user= User.objects.create_user(username=username,email=email, password=password)
                    user.save()

                    #log in user and redirect to settings page
                    user_login=auth.authenticate(username=username, password=password)
                    auth.login(request,user_login)
                    
                    #create new user profile 
                    user_model=User.objects.get(username=username)
                    new_profile= Profile.objects.create(user=user_model, id_user=user_model.id)  
                    new_profile.save()
                    return redirect('settings')
            else:
                messages.error(request,'password not matching !')
                return redirect('signup')
    
class SigninView(View):
    template_name = 'signin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")
            return redirect("signin") 
    
@method_decorator(login_required(login_url='signin'), name='dispatch')
class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return redirect('signin')   


