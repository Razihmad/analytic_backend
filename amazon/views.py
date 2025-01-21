from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from base.response import status_200

# Create your views here.


class TryApi(APIView):
    def get(self, request):
        from amazon.tasks import testing_tasks
        print("tasksuing iansnjasdfk")
        testing_tasks.apply_async(countdown=10)
        print("tasksuing iansnjasdfk")


        return status_200(message="Hello World", data={"name": "Razi"})


class FetchSellerCentralDataAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from amazon.tasks import fetch_seller_central_data
        fetch_seller_central_data.delay()
        return status_200(message="We are preparing your data for visualization")
