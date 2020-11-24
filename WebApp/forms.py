from wtforms import Form, StringField, IntegerField, validators, RadioField, PasswordField, BooleanField
import email_validator
from wtforms.fields.html5 import EmailField, DateField
from wtforms_components import DateRange
import datetime
# to validate the format of the sheet and the presence of the sheet in the url provided
from apis.gsheet import validate_sheet
from validator_collection import checkers


# register form
class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(
        min=6, max=30), validators.DataRequired()])
    username = StringField('Username', [validators.DataRequired(), validators.Regexp(
        regex="^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]$", message="Minimum 8-20 characters, special symbol (. or _) in between")])
    email = EmailField('Email Address', [
                       validators.DataRequired(), validators.Email()])
    password = PasswordField('New Password', [
        validators.Regexp(regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$",
                          message="Minimum eight characters, at least one uppercase letter, one lowercase letter and one number"),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# login form
class LoginForm(Form):
    username = StringField('Username', [validators.Length(
        min=4, max=25), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

# task form


class TaskForm(Form):
    name = StringField('Task Name', [validators.Length(
        min=8, max=50), validators.DataRequired()])
    description = StringField(
        'Description', [validators.Length(min=10, max=300)])

    start_date = DateField("Start Date", validators=[DateRange(
        min=datetime.date.today()), validators.DataRequired()], format='%Y-%m-%d')

    end_date = DateField("End Date", validators=[DateRange(
        min=datetime.date.today()), validators.DataRequired()], format='%Y-%m-%d')

    sheet_name = StringField('Sheet Name', [validators.DataRequired()])
    sheet_url = StringField('Sheet Url', [validators.DataRequired()])
    bot_assigned = RadioField('Bot Type', choices=[
                              'Monitor the Excel Sheet', 'Document PPT Detection', 'Synopsis Document Detection'])

    # it takes two paramters the self and the field which is to be validated.
    def validate_end_date(self, field):
        # and the function name should be validate_{{ field to be validated }}

        if (field.data >= self.start_date.data):
            return True
        else:

            # this is the error which is thrown when the validation error occurred while submitting.
            raise validators.ValidationError(
                "End Date should not be earlier than the Start Date")

    # field is sheet_url and fiedl1 is sheet_name
    def validate_sheet_url(self, field):
        doc = 0
        if "document" in self.bot_assigned.data.lower():
            doc = 1

        if checkers.is_url(field.data) and validate_sheet(self.sheet_url.data, self.sheet_name.data, doc)[0]:

            return True
        else:
            status, response = validate_sheet(
                self.sheet_url.data, self.sheet_name.data, doc)

            if status is False:  # means something is wrong.
                error = "Invalid URL"
                error = " ".join(response.split("_"))
                if "NOT FOUND" in error:
                    error = "GSheet URL Not Found"
                # elif "PERMISSION" in error:
                #     error=error.title()
                # else:
                #     error =" "
            raise validators.ValidationError(error)

    def validate_sheet_name(self, field):

        if "document" in self.bot_assigned.data.lower():
            status, response = validate_sheet(
                self.sheet_url.data, self.sheet_name.data, doc=1)
        else:
            status, response = validate_sheet(
                self.sheet_url.data, self.sheet_name.data)

        if status is False:  # means something is wrong.
            error = " ".join(response.split("_"))
            if "NOT FOUND" in error:
                error = "Sheet Not Found"
            raise validators.ValidationError(error.title())
        return True
