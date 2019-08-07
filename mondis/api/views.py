from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from api.constants import CANDIDATE_PERSON
from api.models import Person, Slot, Event
from api.utils import validate_person_input, validate_new_slot_input


@method_decorator(csrf_exempt, name='dispatch')
class AddPerson(View):
    """
    Helper view used for adding users
    """
    def post(self, request):
        result, message, data = validate_person_input(request)
        if not result:
            return JsonResponse({
                'success': False,
                'message': message
            })

        try:
            Person.objects.create(
                username=data['username'],
                person_type=data['person_type']
            )
        except IntegrityError:
            return JsonResponse({'success': False, 'message': _('This person already exists')}, status=400)

        return JsonResponse({'success': True})


@method_decorator(csrf_exempt, name='dispatch')
class AddSlot(View):
    """
    View used for registering slots
    """
    def post(self, request):
        result, message, data = validate_new_slot_input(request)
        if not result:
            return JsonResponse({
                'success': False,
                'message': message
            })

        # check first if that slot is assigned to some other candidate
        if data['user'].person_type == CANDIDATE_PERSON and Slot.objects.filter(hour=data['hour'],
                                                                                added_at=data['date_object'],
                                                                                added_by__person_type=CANDIDATE_PERSON):
            return JsonResponse({'success': False, 'message': _('This slot is taken')}, status=400)

        try:
            Slot.objects.create(
                hour=data['hour'],
                added_by=data['user'],
                added_at=data['date_object']
            )
        except IntegrityError:
            return JsonResponse({'success': False, 'message': _('This slot already exists')}, status=400)

        return JsonResponse({'success': True})


class EventList(View):
    """
    View used for getting list of the scheduled events
    """
    def get(self, request):
        candidate = request.GET.get('candidate', None)
        interviewers = request.GET.getlist('interviewer')

        filter_fields = {}

        if candidate is not None:
            filter_fields['{}__{}'.format('users', 'username')] = candidate
        elif interviewers:
            filter_fields['{}__{}__{}'.format('users', 'username', 'in')] = interviewers
        else:
            return JsonResponse({'success': True, 'message': 'Candidate or interviewer list should be set'}, safe=False)

        queryset = Event.objects.filter(**filter_fields)

        events = []
        for event in queryset:
            persons = []
            for person in event.users.all():
                persons.append({
                    'username': person.username,
                    'type': person.get_person_type_display()
                })

            events.append({
                'hour': event.slot.hour,
                'date': event.slot.added_at,
                'users': persons
            })

        return JsonResponse({'success': True, 'data': events}, safe=False)
