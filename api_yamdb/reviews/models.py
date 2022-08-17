from django.contrib.auth.models import AbstractUser
from django.db import models


USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLES_CHOICES = [
    (USER, 'user'),
    (ADMIN, 'admin'),
    (MODERATOR, 'moderator'),
]


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        choices=ROLES_CHOICES,
        default=USER,
        max_length=300
    )

    email = models.EmailField(
        'E-Mail',
        unique=True,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('-date_joined',)

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.is_staff or self.role in [ADMIN]

    @property
    def is_moderator(self):
        return self.is_admin or self.role in [MODERATOR]


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.PositiveSmallIntegerField()
    description = models.TextField(max_length=512,
                                   blank=True,
                                   null=True,
                                   default='')
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles",
    )
    genre = models.ManyToManyField(to=Genre)

    class Meta:
        ordering = ('-year',)

    def __str__(self):
        return self.name[:15]


class Review(models.Model):

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    score = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="review"
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return f"Автор {self.author}текст {self.text}"
