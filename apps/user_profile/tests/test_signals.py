# import uuid
#
# from django.contrib.auth import get_user_model
# from django.test import TestCase
#
# from apps.user_profile.models import Profile
#
# User = get_user_model()
#
#
# # 유저 생성시 프로필
# class UserProfileSignalTest(TestCase):
#     def test_profile_created_when_user_created(self):
#         unique_id = uuid.uuid4()
#
#         user = User.objects.create_user(
#             email=f"test_{unique_id}@test.com",
#             password="testpassword1234",
#             nickname=f"test_{unique_id}",
#         )
#
#         self.assertTrue(Profile.objects.filter(user=user).exists())
#         self.assertEqual(user.profile.user, user)
