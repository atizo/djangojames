from django.forms.widgets import DateInput, TimeInput, DateTimeInput

class Html5DateInput(DateInput):
    input_type = 'date'

    def __init__(self):
        super(Html5DateInput, self).__init__(format="%Y-%m-%d")

class Html5TimeInput(TimeInput):
    input_type = 'time'

    def __init__(self):
        super(Html5TimeInput, self).__init__(format="%H:%M")

class Html5DateTimeInput(DateTimeInput):
    input_type = 'datetime-local'

    def __init__(self):
        super(Html5DateTimeInput, self).__init__(format="%Y-%m-%dT%H:%M")