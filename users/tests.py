from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from .models import CustomUser, FriendRequest

class UserTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_search_url = reverse('search')
        self.friend_request_url = reverse('friend-request')
        self.pending_requests_url = reverse('pending-friend-requests')
        self.friend_list_url = reverse('friends')

        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            # 'password_confirm': 'testpass123'
        }

        self.user1 = CustomUser.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.user2 = CustomUser.objects.create_user(username='user2', email='user2@example.com', password='password123')


    @patch('users.views.CustomUser.objects.filter')
    def test_signup_with_existing_email(self, mock_filter):
        """
        Ensure we can't signup with an email that already exists.
        """
        mock_filter.return_value.exists.return_value = True
        response = self.client.post(self.signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('users.views.CustomUser.objects.get')
    def test_login(self, mock_get):
        """
        Ensure we can login with a created user.
        """
        user = CustomUser.objects.create_user(**self.user_data)
        mock_get.return_value = user
        user.check_password = lambda x: x == self.user_data['password']  # Simulate check_password
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logged in successfully')

    @patch('users.views.CustomUser.objects.get')
    def test_login_with_invalid_credentials(self, mock_get):
        """
        Ensure login fails with invalid credentials.
        """
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        mock_get.return_value = mock_user
        login_data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('users.views.CustomUser.objects.get')
    def test_login_with_nonexistent_user(self, mock_get):
        """
        Ensure login fails for a user that does not exist.
        """
        mock_get.side_effect = CustomUser.DoesNotExist
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'Testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """
        Ensure we can logout a logged-in user.
        """
        self.client.force_authenticate(user=CustomUser.objects.create_user(**self.user_data))
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully logged out')

    @patch('users.views.CustomUser.objects.get')
    def test_send_friend_request(self, mock_get):
        """
        Ensure we can send a friend request.
        """
        from_user = CustomUser.objects.create_user(**self.user_data)
        to_user_data = {
            'username': 'frienduser',
            'email': 'friend@example.com',
            'password': 'Friendpass123'
        }
        to_user = CustomUser.objects.create_user(**to_user_data)
        self.client.force_authenticate(user=from_user)
        friend_request_data = {
            'email': to_user.email,
            'action': 'send'
        }
        response = self.client.post(self.friend_request_url, friend_request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Friend request sent')

    @patch('users.views.CustomUser.objects.get')
    def test_accept_friend_request(self, mock_get):
        """
        Ensure we can accept a friend request.
        """
        from_user = CustomUser.objects.create_user(**self.user_data)
        to_user_data = {
            'username': 'frienduser',
            'email': 'friend@example.com',
            'password': 'Friendpass123'
        }
        to_user = CustomUser.objects.create_user(**to_user_data)
        FriendRequest.objects.create(from_user=to_user, to_user=from_user, status='pending')
        self.client.force_authenticate(user=from_user)
        friend_request_data = {
            'email': to_user.email,
            'action': 'accept'
        }
        response = self.client.post(self.friend_request_url, friend_request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Friend request accepted')

    def test_reject_friend_request(self):
        """
        Ensure we can reject a friend request.
        """
        from_user = CustomUser.objects.create_user(**self.user_data)
        to_user_data = {
            'username': 'frienduser',
            'email': 'friend@example.com',
            'password': 'Friendpass123'
        }
        to_user = CustomUser.objects.create_user(**to_user_data)
        FriendRequest.objects.create(from_user=to_user, to_user=from_user, status='pending')
        self.client.force_authenticate(user=from_user)
        friend_request_data = {
            'email': to_user.email,
            'action': 'reject'
        }
        response = self.client.post(self.friend_request_url, friend_request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Friend request rejected')

    def test_view_pending_friend_requests(self):
        """
        Ensure we can view pending friend requests.
        """
        user = CustomUser.objects.create_user(**self.user_data)
        friend_user = CustomUser.objects.create_user(
            username='frienduser', email='friend@example.com', password='Friendpass123')
        FriendRequest.objects.create(from_user=friend_user, to_user=user, status='pending')
        self.client.force_authenticate(user=user)
        response = self.client.get(self.pending_requests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data), 1)
        # self.assertEqual(response.data[0]['from_user'], friend_user.id)

    def test_view_friend_list(self):
        """
        Ensure we can view the friend list.
        """
        user = CustomUser.objects.create_user(**self.user_data)
        friend_user = CustomUser.objects.create_user(
            username='frienduser', email='friend@example.com', password='Friendpass123')
        FriendRequest.objects.create(from_user=user, to_user=friend_user, status='accepted')
        self.client.force_authenticate(user=user)
        response = self.client.get(self.friend_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data), 1)
        # self.assertEqual(response.data[0]['id'], friend_user.id)

    @patch('users.views.CustomUser.objects.filter')
    def test_search_users_by_email(self, mock_filter):
        """
        Ensure we can search users by email.
        """
        user = CustomUser.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        search_data = {'search_keyword': user.email}
        mock_filter.return_value = [user]
        response = self.client.get(self.user_search_url, search_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
