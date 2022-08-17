from rest_framework import (mixins,
                            viewsets,
                            status,
                            permissions,
                            filters)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import (api_view,
                                       permission_classes,
                                       action)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

from reviews.models import Category, Genre, Title, User

from .permissions import AdminOrReadOnly, AdminOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCreateSerializer,
    UserSignUpSerializer,
    EmailConfirmationSerializer,
    UsersSerializer,
)
from .filters import TitleFilter


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_signup(request):
    serializer = UserSignUpSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data.get('username')
    )
    confirmation_code = default_token_generator.make_token(user=user)
    send_mail(
        'CONFIRMATION CODE',
        message=f'This is your confirmation code: {confirmation_code}',
        from_email=None,
        recipient_list=[serializer.validated_data.get('email')],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    serializer = EmailConfirmationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data.get('username'))
    token = AccessToken.for_user(user)
    return Response({'token': str(token)},
                    status=status.HTTP_200_OK
                    )


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Title.objects.all()
    lookup_field = 'id'
    search_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleSerializer
        return TitleCreateSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AdminOnly,)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me',
    )
    def me_view(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = UsersSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if user.role == 'user' and 'role' in serializer.initial_data:
                serializer.validated_data.pop('role')
            serializer.save()
            return Response(serializer.data)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
