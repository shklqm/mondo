import json
from datetime import datetime
from json import JSONDecodeError

from django.utils.translation import gettext_lazy as _

from api.constants import CANDIDATE_PERSON, INTERVIEWER_PERSON, HOUR_LIST, USERNAME_MAX_LENGTH
from api.models import Person


def validate_person_input(request):
    """
    Parse the given request and convert it to a triplet containing success, message error
    and dict of username and person type

    :param request:
    :return (boolean, str, dict)
    """
    try:
        json_data = json.loads(request.body)
    except JSONDecodeError:
        return False, _('Invalid request body'), None

    try:
        username = json_data['username']
        person_type = json_data['person_type']
        if len(username) > USERNAME_MAX_LENGTH:
            return False, _('Username too big'), None

        if person_type != CANDIDATE_PERSON and person_type != INTERVIEWER_PERSON:
            return False, _('Invalid person type'), None
    except KeyError:
        return False, _('Invalid request'), None

    return True, None, {
        'username': username,
        'person_type': person_type
    }


def validate_new_slot_input(request):
    """
    Parse the given request and convert it to a triplet containing success, message error
    and dict of hour, date and user

    :param request:
    :return (boolean, str, dict)
    """
    try:
        json_data = json.loads(request.body)
    except JSONDecodeError:
        return False, _('Invalid request body'), None

    try:
        hour = json_data['hour']
        username = json_data['username']
        date = json_data['date']

        if hour not in HOUR_LIST:
            return False, _('Invalid hour'), None

        try:
            date_object = datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            return False, _('Invalid date. Expected format: dd/mm/yyyy'), None

        try:
            user = Person.objects.get(username=username)
        except Person.DoesNotExist:
            return False, _('Invalid user'), None

    except KeyError:
        return False, _('Invalid request'), None

    return True, None, {
        'hour': hour,
        'date_object': date_object,
        'user': user
    }

