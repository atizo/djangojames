from django.forms.widgets import DateInput

class Html5DateInput(DateInput):
    input_type = 'date'

    def __init__(self):
        super(Html5DateInput, self).__init__(format="%Y-%m-%d")

