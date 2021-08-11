from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Group name"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Slug"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description"
    )

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


class Post(models.Model):
    group = models.ForeignKey(Group,
                              null=True,
                              blank=True,
                              verbose_name="Group",
                              on_delete=models.SET_NULL)
    text = models.TextField(verbose_name="Text")
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name="Date")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             related_name="comments",
                             on_delete=models.CASCADE,
                             verbose_name="Post"
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Author")
    text = models.TextField(verbose_name="Comment text")
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name="Comment_date")

    class Meta:
        ordering = ("-created",)
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    class Meta:
        verbose_name = "Follow"
        verbose_name_plural = "Follows"

    def __str__(self):
        return f"{self.user} following {self.author}"
