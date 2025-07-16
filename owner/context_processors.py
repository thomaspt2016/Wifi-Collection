from common.models import Profile

def profile_context(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        return {'pass': profile}
    else:
        return {'pass': None}