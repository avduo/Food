from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
       UserProfile.objects.create(user=instance)
       # print('User created')
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            # print('User updateded')
            profile.save()
        except:
            # Create the User profile if it does not exist
            UserProfile.objects.create(user=instance)
            # print('Profile did not exist, but I created one')

@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    print(instance.username, 'this user is being saved')