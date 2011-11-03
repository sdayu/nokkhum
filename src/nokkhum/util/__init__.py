from twisted.web import resource

class PageNotFoundError(resource.Resource):

    def render_GET(self, request):
        return 'Page Not Found!'