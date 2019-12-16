from django.db import models
from django.conf import settings

from django.contrib.auth.models import User


# User profile
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    date_of_birht = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    def __str__(self):
        return 'Profile for user: {}'.format(self.user.username)


class Contact(models.Model):
    user_from = models.ForeignKey(
        'auth.User',
        related_name='rel_from_set',
        on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        'auth.User',
        related_name='rel_to_set',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{} follows {}'.format(
            self.user_from,
            self.user_to,
        )


# Такой способ добавления атрибута рекомендуется использовать только в особенных случаях!
# Если модель User определена в нашем приложении, мы можем добавить в нее поле напрямую.
# В нашем случае это невозможно, т.к. используется модель пользователя из django.contrib.auth.
# Динамическое добавление поля following в модель User
User.add_to_class(
    'following',
    models.ManyToManyField(
        'self',
        through=Contact,
        related_name='followers',
        symmetrical=False
    )
)
