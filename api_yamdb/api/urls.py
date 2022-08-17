from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet,
                       GenreViewSet,
                       TitleViewSet,
                       user_signup,
                       get_jwt_token,
                       UsersViewSet,
                       )
from reviews.views import ReviewsViewSet, CommentsViewSet

app_name = "api_yamdb"

api_router = DefaultRouter()
api_router.register("categories", CategoryViewSet, basename='categoryviewset')
api_router.register("genres", GenreViewSet, basename='genreviewset')
api_router.register("titles", TitleViewSet, basename='titleviewset')
api_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='review'
)
api_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)
# api_router.register('users/me', MeViewSet, basename='meviewset')
api_router.register('users', UsersViewSet, basename='usersviewset')

urlpatterns = [
    path("", include(api_router.urls)),
    path("auth/signup/", user_signup, name="signup"),
    path(
        "auth/token/", get_jwt_token, name="get_token"
    ),
]
