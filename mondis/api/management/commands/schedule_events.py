from django.core.management.base import BaseCommand

from api.constants import INTERVIEWER_PERSON
from api.models import Slot, Event, Person


class Command(BaseCommand):
    """
    Command used for matching candidate and interviewers and creating the
    related events. Interviewers who had not added any slot, are assigned to existing events.
    """
    def handle(self, *args, **options):
        # create pairs in the format: {(added_at, hour): ([person1, person2, ...], slot), ...}
        pairs = {}

        for slot in Slot.objects.all():
            key = (slot.added_at, slot.hour)
            if key not in pairs:
                pairs[key] = ([], slot)
            pairs[key][0].append(slot.added_by)

        # create events where at least two persons exist
        events = []
        for key, value in pairs.items():
            persons, slot = value
            if len(persons) >= 2:
                event = Event.objects.create(slot=slot)
                events.append(event)

                # add persons
                for person in persons:
                    event.users.add(person)

                event.save()

        if not events:
            return

        # get lonely interviewers and distribute them to other events
        single_interviewers = list(Person.objects.filter(event=None, person_type=INTERVIEWER_PERSON))
        interviewer_per_event = len(single_interviewers) // len(events)

        for event in events:
            count = 0
            while single_interviewers and count < interviewer_per_event:
                event.users.add(single_interviewers.pop())
                count += 1

            event.save()
