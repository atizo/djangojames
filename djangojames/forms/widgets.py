from django.forms.widgets import DateInput
from django.forms.widgets import TimeInput

class Html5DateInput(DateInput):
    input_type = 'date'

    def __init__(self):
        super(Html5DateInput, self).__init__(format="%Y-%m-%d")

class Html5TimeInput(TimeInput):
    input_type = 'time'

    def __init__(self):
        super(Html5TimeInput, self).__init__(format="%H:%M")