from rest_framework.test import APITransactionTestCase


class BaseTestMixin(APITransactionTestCase):
    """
    Base class for test cases that sets up the test environment.
    """

    def setUp(self):
        """
        Set up the test environment by creating a user and a client.
        """
        # Create a client for making API requests
        self.client = self.create_client()

    def create_client(self):
        """
        Create a new client for making API requests.

        Returns:
            APIClient: The created client instance.
        """
        from rest_framework.test import APIClient
        return APIClient()

    def tearDown(self) -> None:
        return super().tearDown()
