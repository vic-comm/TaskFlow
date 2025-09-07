import pytest
from django.core import mail
from django.utils.timezone import now, timedelta
from .models import TaskDependency
from django.core.exceptions import ValidationError

