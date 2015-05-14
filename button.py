class Button:
    def __init__(self, name, systemcode, unitcode, state, repeats):
        self.name = name
        self.systemcode = systemcode
        self.unitcode = unitcode
        self.state = state
        self.repeats = repeats
        self.protocol = u'elro_800_switch'

    def match(self, obj):
        try:
            if obj['message']['systemcode'] != self.systemcode:
                return ''
            if obj['message']['unitcode'] != self.unitcode:
                return ''
            if obj['message']['state'] != self.state:
                return ''
            if obj['protocol'] != self.protocol:
                return ''
            if obj['repeats'] != self.repeats:
                return ''
        except KeyError, e:
            return ''

        return self.name


        
        

            
