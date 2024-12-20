# Third Party
from rest_framework.views import APIView
from rest_framework.response import Response

# Authentication
from authentication.services import get_amazon_login_uri


# Create your views here.
class AmazonLogin(APIView):
    def get(self, request):
        url = get_amazon_login_uri(marketplace="US")
        return Response({"url": url})
        # return {"message": "Hello, world!"}


class AmazonCallback(APIView):
    def get(self, request):
        selling_partner_id = request.GET.get("selling_partner_id")
        spapi_oauth_code = request.GET.get("spapi_oauth_code")
        state = request.GET.get("state")
        print(spapi_oauth_code, state, selling_partner_id)
        return Response({"message": "Hello, world!"})
