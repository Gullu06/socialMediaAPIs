# users/urls.py
from django.urls import path # type: ignore
from .views import LogoutView, PendingFriendRequestsView, SignupView, LoginView, UserSearchView, FriendRequestView, FriendListView, root_view

urlpatterns = [
    path('', root_view, name='root'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('pending-friend-requests/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
