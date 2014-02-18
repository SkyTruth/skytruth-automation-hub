import endpoints

from geofeed_api import GeoFeedApi
from taskqueue_api import TaskQueueApi
from test_api import TestApi

app = endpoints.api_server([GeoFeedApi, TaskQueueApi, TestApi])