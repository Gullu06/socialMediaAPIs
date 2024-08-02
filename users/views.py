from rest_framework import generics, status # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework.pagination import PageNumberPagination # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.shortcuts import get_object_or_404 # type: ignore
from django.db.models import Q # type: ignore
from django.shortcuts import redirect # type: ignore
from .models import CustomUser, FriendRequest
from .serializers import FriendRequestActionSerializer, LoginSerializer, LogoutSerializer, SearchSerializer, SignupSerializer, UserSerializer, FriendRequestSerializer

def root_view(request):
    return redirect('/api/users/signup/')

class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'error': 'Already authenticated'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]  # Allow anyone to access login

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'message': 'Already logged in'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if user:
            login(request, user)
            return Response({'message': 'Logged in successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class UserSearchPagination(PageNumberPagination):
    page_size = 10

class UserSearchView(generics.GenericAPIView):
    serializer_class = SearchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserSearchPagination

    queryset = CustomUser.objects.none()

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        search_keyword = serializer.validated_data['search_keyword']

        if "@" in search_keyword:
            queryset = CustomUser.objects.filter(email__iexact=search_keyword)
        else:
            queryset = CustomUser.objects.filter(username__icontains=search_keyword)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FriendRequestView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestActionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_user = request.user
        email = serializer.validated_data['email']
        action = serializer.validated_data['action']

        to_user = get_object_or_404(CustomUser, email=email)

        if CustomUser.objects.filter(
                Q(sent_requests__from_user=from_user, sent_requests__to_user=to_user, sent_requests__status='accepted') |
                Q(sent_requests__from_user=to_user, sent_requests__to_user=from_user, sent_requests__status='accepted')
        ).exists():
            return Response({'error': 'You are already friends'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'send':
            if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
                return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
            if FriendRequest.objects.filter(from_user=to_user, to_user=from_user, status='pending').exists():
                return Response({'error': 'Friend request already received'}, status=status.HTTP_400_BAD_REQUEST)
            FriendRequest.objects.create(from_user=from_user, to_user=to_user, status='pending')
            return Response({'message': 'Friend request sent'}, status=status.HTTP_200_OK)

        elif action == 'accept':
            request_obj = get_object_or_404(FriendRequest, from_user=to_user, to_user=from_user, status='pending')
            request_obj.status = 'accepted'
            request_obj.save()
            from_user.friends.add(to_user)
            to_user.friends.add(from_user)
            return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)

        elif action == 'reject':
            request_obj = get_object_or_404(FriendRequest, from_user=to_user, to_user=from_user, status='pending')
            request_obj.status = 'rejected'
            request_obj.save()
            return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

class PendingFriendRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

class FriendListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        friends = CustomUser.objects.filter(
            Q(sent_requests__from_user=user, sent_requests__status='accepted') |
            Q(received_requests__to_user=user, received_requests__status='accepted')
        ).distinct()
        return friends
