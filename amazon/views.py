from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from amazon.services import start_fetching_seller_central_data
from base.response import status_200

# Create your views here.
import logging

logger = logging.getLogger(__name__)


class TryApi(APIView):
    def get(self, request):
        # from amazon.tasks import testing_tasks
        # print("tasksuing iansnjasdfk")
        # testing_tasks.apply_async(countdown=10)
        # print("tasksuing iansnjasdfk")
        logger.info(f"this is kiahsjkdjhf {request=}")

        return status_200(message="Hello World", data={"name": "Razi"})


class FetchSellerCentralDataAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        amazon_seller_id = request.GET.get("selling_partner_id")
        start_fetching_seller_central_data(user_id=user_id, amazon_seller_id=amazon_seller_id)
        return status_200(message="We are preparing your data for visualization")
