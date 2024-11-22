# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'get_following_count', 'get_followers_count'
    )
    list_select_related = ('profile',)

    def get_following_count(self, instance):
        return instance.profile.following.count()
    get_following_count.short_description = 'Following'

    def get_followers_count(self, instance):
        return instance.profile.followers.count()
    get_followers_count.short_description = 'Followers'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)

# Unregister the original User admin
admin.site.unregister(User)
# Register the new User admin
admin.site.register(User, UserAdmin)

# Optional: Register Profile model separately if you want to manage it directly
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'get_following_count', 'get_followers_count')
    search_fields = ('user__username', 'bio')
    list_filter = ('user__is_active',)

    def get_following_count(self, obj):
        return obj.following.count()
    get_following_count.short_description = 'Following'

    def get_followers_count(self, obj):
        return obj.followers.count()
    get_followers_count.short_description = 'Followers'
