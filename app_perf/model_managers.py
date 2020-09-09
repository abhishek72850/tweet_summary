from django.contrib.auth.models import BaseUserManager
from app_perf.models import User, Admins, Subscribers


class UserManager(BaseUserManager):

    def get_by_natural_key(self, email):
        return self.get(email=email)


class AdminsManager(BaseUserManager):

    def create_admin(self, first_name, last_name, email, is_staff, is_active, password=None):
        if email is None:
            raise TypeError('Users must have an email address.')
        student = Admins(first_name=first_name, last_name=last_name,
                         email=self.normalize_email(email),
                         is_staff=is_staff, is_active=is_active)
        student.set_password(password)
        student.save()
        return student


class SubscribersManager(BaseUserManager):

    def create_subscriber(self, email, password=None):
        if email is None:
            raise TypeError('Users must have an email address.')
        employee = Subscribers(email=self.normalize_email(email))
        employee.set_password(password)
        employee.save()
        return employee
