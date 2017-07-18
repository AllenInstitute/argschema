'''marshmallow fields related to choosing amongst a set of options'''
import marshmallow as mm


class OptionList(mm.fields.Field):
    '''OptionList is a marshmallow field which enforces that this field
       is one of a finite set of options.
       OptionList(options,*args,**kwargs) where options is a list of
       json compatible options which this option will be enforced to belong
    '''
    def __init__(self, options, *args, **kwargs):
        self.options = options
        super(OptionList, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        return value

    def _validate(self, value):
        if value not in self.options:
            raise mm.ValidationError("%s is not a valid option" % value)

        return value
