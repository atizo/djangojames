from django.forms.widgets import DateInput

class Html5DateInput(DateInput):
    input_type = 'date'