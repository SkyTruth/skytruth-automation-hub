import endpoints
import settings

class EndpointsHelper ():
    @staticmethod
    def authenticate():
        current_user = endpoints.get_current_user()
        if settings.ENFORCE_AUTH and current_user is None:
            raise endpoints.UnauthorizedException('Invalid oauth client id')

    @staticmethod
    def message2dict (message):
        return {f.name: message.get_assigned_value(f.name) 
            for f in message.all_fields() 
            if message.get_assigned_value(f.name) is not None}

