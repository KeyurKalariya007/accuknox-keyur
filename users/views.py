from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer,FriendRequestSerializer,LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FriendRequest
from django.core.cache import cache
from django.http import HttpResponseForbidden

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email__iexact=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=400)



class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', '')
        return User.objects.filter(Q(email__iexact=keyword) | Q(name__icontains=keyword))



class FriendRequestCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        cache_key = f"friend_request_count:{user_id}"
        count = cache.get(cache_key, 0)
        if count >= 3:
            return HttpResponseForbidden("Rate limit exceeded. You can only send 3 friend requests per minute.")
        
        serializer = FriendRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            cache.set(cache_key, count + 1, 60)  # Increase count and set expiry to 60 seconds
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class FriendRequestHandleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        try:
            friend_request = FriendRequest.objects.get(pk=pk, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'accept':
            friend_request.status = 'accepted'
            friend_request.save()
            return Response({'status': 'accepted'}, status=status.HTTP_200_OK)
        elif action == 'reject':
            friend_request.status = 'rejected'
            friend_request.save()
            return Response({'status': 'rejected'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)



class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        accepted_requests = FriendRequest.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) & Q(status='accepted')
        )
        friends = [req.from_user if req.to_user == user else req.to_user for req in accepted_requests]
        return friends

class PendingFriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user, status='pending')
