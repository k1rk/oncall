import datetime

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.schedules.models import CustomOnCallShift, OnCallScheduleCalendar, OnCallScheduleWeb

invalid_field_data_1 = {
    "frequency": None,
}

invalid_field_data_2 = {
    "start": datetime.datetime.now(),
}

invalid_field_data_3 = {
    "by_day": ["QQ", "FR"],
}

invalid_field_data_4 = {
    "by_month": [13],
}

invalid_field_data_5 = {
    "by_monthday": [35],
}

invalid_field_data_6 = {
    "interval": 0,
}

invalid_field_data_7 = {
    "type": "invalid_type",
}

invalid_field_data_8 = {
    "until": "not-a-date",
}


@pytest.mark.django_db
def test_get_on_call_shift(make_organization_and_user_with_token, make_on_call_shift, make_schedule):
    organization, user, token = make_organization_and_user_with_token()
    client = APIClient()

    data = {
        "start": datetime.datetime.now().replace(microsecond=0),
        "duration": datetime.timedelta(seconds=7200),
    }
    schedule = make_schedule(organization, schedule_class=OnCallScheduleCalendar)
    on_call_shift = make_on_call_shift(
        organization=organization, shift_type=CustomOnCallShift.TYPE_SINGLE_EVENT, **data
    )
    on_call_shift.users.add(user)
    schedule.custom_on_call_shifts.add(on_call_shift)

    url = reverse("api-public:on_call_shifts-detail", kwargs={"pk": on_call_shift.public_primary_key})

    response = client.get(url, format="json", HTTP_AUTHORIZATION=f"{token}")

    result = {
        "id": on_call_shift.public_primary_key,
        "team_id": None,
        "name": on_call_shift.name,
        "type": "single_event",
        "time_zone": None,
        "level": 0,
        "start": on_call_shift.start.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": int(on_call_shift.duration.total_seconds()),
        "users": [user.public_primary_key],
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == result


@pytest.mark.django_db
def test_get_override_on_call_shift(make_organization_and_user_with_token, make_on_call_shift, make_schedule):
    organization, user, token = make_organization_and_user_with_token()
    client = APIClient()

    schedule = make_schedule(organization, schedule_class=OnCallScheduleWeb)
    data = {
        "start": datetime.datetime.now().replace(microsecond=0),
        "duration": datetime.timedelta(seconds=7200),
        "schedule": schedule,
    }
    on_call_shift = make_on_call_shift(organization=organization, shift_type=CustomOnCallShift.TYPE_OVERRIDE, **data)
    on_call_shift.users.add(user)

    url = reverse("api-public:on_call_shifts-detail", kwargs={"pk": on_call_shift.public_primary_key})

    response = client.get(url, format="json", HTTP_AUTHORIZATION=f"{token}")

    result = {
        "id": on_call_shift.public_primary_key,
        "team_id": None,
        "name": on_call_shift.name,
        "type": "override",
        "time_zone": None,
        "start": on_call_shift.start.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": int(on_call_shift.duration.total_seconds()),
        "users": [user.public_primary_key],
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.data == result


@pytest.mark.django_db
def test_create_on_call_shift(make_organization_and_user_with_token):

    organization, user, token = make_organization_and_user_with_token()
    client = APIClient()

    url = reverse("api-public:on_call_shifts-list")

    start = datetime.datetime.now()
    until = start + datetime.timedelta(days=30)
    data = {
        "team_id": None,
        "name": "test name",
        "type": "recurrent_event",
        "level": 1,
        "start": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": 10800,
        "users": [user.public_primary_key],
        "week_start": "MO",
        "frequency": "weekly",
        "interval": 2,
        "until": until.strftime("%Y-%m-%dT%H:%M:%S"),
        "by_day": ["MO", "WE", "FR"],
    }

    response = client.post(url, data=data, format="json", HTTP_AUTHORIZATION=f"{token}")
    on_call_shift = CustomOnCallShift.objects.get(public_primary_key=response.data["id"])

    result = {
        "id": on_call_shift.public_primary_key,
        "team_id": None,
        "name": data["name"],
        "type": "recurrent_event",
        "time_zone": None,
        "level": data["level"],
        "start": data["start"],
        "duration": data["duration"],
        "frequency": data["frequency"],
        "interval": data["interval"],
        "until": data["until"],
        "week_start": data["week_start"],
        "by_day": data["by_day"],
        "users": [user.public_primary_key],
        "by_month": None,
        "by_monthday": None,
    }

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == result


@pytest.mark.django_db
def test_create_override_on_call_shift(make_organization_and_user_with_token):

    organization, user, token = make_organization_and_user_with_token()
    client = APIClient()

    url = reverse("api-public:on_call_shifts-list")

    start = datetime.datetime.now()
    data = {
        "team_id": None,
        "name": "test name",
        "type": "override",
        "start": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": 10800,
        "users": [user.public_primary_key],
    }

    response = client.post(url, data=data, format="json", HTTP_AUTHORIZATION=f"{token}")
    on_call_shift = CustomOnCallShift.objects.get(public_primary_key=response.data["id"])

    result = {
        "id": on_call_shift.public_primary_key,
        "team_id": None,
        "name": data["name"],
        "type": "override",
        "time_zone": None,
        "start": data["start"],
        "duration": data["duration"],
        "users": [user.public_primary_key],
    }

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == result


@pytest.mark.django_db
def test_update_on_call_shift(make_organization_and_user_with_token, make_on_call_shift, make_schedule):
    organization, user, token = make_organization_and_user_with_token()
    client = APIClient()

    data = {
        "start": datetime.datetime.now().replace(microsecond=0),
        "duration": datetime.timedelta(seconds=7200),
        "frequency": CustomOnCallShift.FREQUENCY_WEEKLY,
        "interval": 2,
        "by_day": ["MO", "FR"],
    }

    schedule = make_schedule(organization, schedule_class=OnCallScheduleCalendar)
    on_call_shift = make_on_call_shift(
        organization=organization, shift_type=CustomOnCallShift.TYPE_RECURRENT_EVENT, **data
    )
    schedule.custom_on_call_shifts.add(on_call_shift)

    url = reverse("api-public:on_call_shifts-detail", kwargs={"pk": on_call_shift.public_primary_key})

    data_to_update = {
        "duration": 14400,
        "users": [user.public_primary_key],
        "by_day": ["MO", "WE", "FR"],
    }

    assert int(on_call_shift.duration.total_seconds()) != data_to_update["duration"]
    assert on_call_shift.by_day != data_to_update["by_day"]
    assert len(on_call_shift.users.filter(public_primary_key=user.public_primary_key)) == 0

    response = client.put(url, data=data_to_update, format="json", HTTP_AUTHORIZATION=f"{token}")

    result = {
        "id": on_call_shift.public_primary_key,
        "team_id": None,
        "name": on_call_shift.name,
        "type": "recurrent_event",
        "time_zone": None,
        "level": 0,
        "start": on_call_shift.start.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": data_to_update["duration"],
        "frequency": "weekly",
        "interval": on_call_shift.interval,
        "until": None,
        "week_start": "SU",
        "by_day": data_to_update["by_day"],
        "users": [user.public_primary_key],
        "by_month": None,
        "by_monthday": None,
    }

    assert response.status_code == status.HTTP_200_OK
    on_call_shift.refresh_from_db()

    assert int(on_call_shift.duration.total_seconds()) == data_to_update["duration"]
    assert on_call_shift.by_day == data_to_update["by_day"]
    assert len(on_call_shift.users.filter(public_primary_key=user.public_primary_key)) == 1
    assert response.data == result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data_to_update",
    [
        invalid_field_data_1,
        invalid_field_data_2,
        invalid_field_data_3,
        invalid_field_data_4,
        invalid_field_data_5,
        invalid_field_data_6,
        invalid_field_data_7,
        invalid_field_data_8,
    ],
)
def test_update_on_call_shift_invalid_field(make_organization_and_user_with_token, make_on_call_shift, data_to_update):
    organization, user, token = make_organization_and_user_with_token()
    client = APIClient()

    data = {
        "start": datetime.datetime.now().replace(microsecond=0),
        "duration": datetime.timedelta(seconds=7200),
        "frequency": CustomOnCallShift.FREQUENCY_WEEKLY,
        "interval": 2,
        "by_day": ["MO", "FR"],
    }

    on_call_shift = make_on_call_shift(
        organization=organization, shift_type=CustomOnCallShift.TYPE_RECURRENT_EVENT, **data
    )

    url = reverse("api-public:on_call_shifts-detail", kwargs={"pk": on_call_shift.public_primary_key})

    response = client.put(url, data=data_to_update, format="json", HTTP_AUTHORIZATION=f"{token}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_on_call_shift(make_organization_and_user_with_token, make_on_call_shift):

    organization, user, token = make_organization_and_user_with_token()
    client = APIClient()

    data = {
        "start": datetime.datetime.now().replace(microsecond=0),
        "duration": datetime.timedelta(seconds=7200),
    }
    on_call_shift = make_on_call_shift(
        organization=organization, shift_type=CustomOnCallShift.TYPE_SINGLE_EVENT, **data
    )

    url = reverse("api-public:on_call_shifts-detail", kwargs={"pk": on_call_shift.public_primary_key})

    response = client.delete(url, format="json", HTTP_AUTHORIZATION=f"{token}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(CustomOnCallShift.DoesNotExist):
        on_call_shift.refresh_from_db()
