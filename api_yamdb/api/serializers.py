import datetime

from rest_framework import serializers
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from reviews.models import (Review,
                            Comment,
                            Category,
                            Title,
                            Genre,
                            User)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    title = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Title.objects.all(),
        required=False
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(
                    author_id=user.id, title_id=title_id
            ).exists():
                raise serializers.ValidationError("Вы уже оставляли отзыв.")
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserSignUpSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'me нельзя использовать в качестве username'
            )
        return data

    class Meta:
        model = User
        fields = ('email', 'username')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class EmailConfirmationSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(
        max_length=512,
        write_only=True
    )
    username = serializers.CharField(
        max_length=512,
        write_only=True
    )

    def validate(self, data):
        user = get_object_or_404(
            User,
            username=data['username']
        )
        email_code = data['confirmation_code']
        if not default_token_generator.check_token(user, email_code):
            raise serializers.ValidationError(
                'Неправильный confirmation_code'
            )
        return data

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True,
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if not rating:
            return rating
        return round(rating, 1)


class TitleCreateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        read_only=True,
        required=False,
        default=0
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        read_only_fields = ('rating',)
        model = Title

    def validate_year(self, year):
        if year > datetime.datetime.now().year:
            raise serializers.ValidationError(
                'Нельзя добавлять ещё не вышедшие произведения'
            )
        return year
