"""MODELS AUTHS"""
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from companyshares.models import Shares



class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Хеширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    


class MyUser(AbstractBaseUser, PermissionsMixin):

    class Currencies(models.TextChoices):
        TENGE = 'KZT', 'Tenge'
        RUBLI = 'RUB', 'Rubli'
        EURO = 'EUR', 'Euro'
        DOLLAR = 'USD', 'Dollar'

    email = models.EmailField(
        verbose_name='почта/логин',
        unique=True,
        max_length=200
    )
    nickname = models.CharField(
        verbose_name='ник',
        max_length=120
    )

    shares = models.ManyToManyField(
        to = Shares ,
        verbose_name='ваши акции',
        related_name='share',

    )

    balance = models.DecimalField(
        verbose_name='баланс',
        max_digits=11,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(
        verbose_name='валюта',
        max_length=4,
        choices=Currencies.choices,
        default=Currencies.TENGE
    )
    
    is_active = models.BooleanField(
        default=True
        )
    
    is_staff = models.BooleanField(
        default=False
    )
    objects = MyUserManager()

    @property
    def balance(self) -> float:
        transactions: QuerySet[Transaction] = \
            Transaction.objects.filter(user=self.pk)
        result: float = 0
        for trans in transactions:
            if trans.is_filled:
                result += trans.amout
            else:
                result -= trans.amout
        return result

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        app_label = 'auths'


class Transaction(models.Model):
    user = models.ForeignKey(
        verbose_name='пользователь',
        related_name='transaction',
        to=MyUser,
        on_delete=models.PROTECT

    )
    amout = models.DecimalField(
        verbose_name='сумма',
        max_digits=11,
        decimal_places=2
    )
    datetime_created = models.DateTimeField(
        verbose_name='дата транзакции',
        auto_now_add=True,
    )
    is_filled = models.BooleanField(
        verbose_name='пополнение',
        default=False
    )

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'