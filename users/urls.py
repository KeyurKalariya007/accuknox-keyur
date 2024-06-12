from django.urls import path
from .views import RegisterView, LoginView, UserSearchView, PendingFriendRequestListView,FriendListView
from .views import FriendRequestCreateView, FriendRequestHandleView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('friend-request/', FriendRequestCreateView.as_view(), name='friend_request'),
    path('friend-request/<int:pk>/', FriendRequestHandleView.as_view(), name='handle_friend_request'),
    path('friends/', FriendListView.as_view(), name='friends_list'),
    path('pending-requests/', PendingFriendRequestListView.as_view(), name='pending_requests_list'),
]
