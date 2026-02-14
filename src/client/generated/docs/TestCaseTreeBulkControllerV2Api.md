# src.client.generated.TestCaseTreeBulkControllerV2Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**drag_and_drop**](TestCaseTreeBulkControllerV2Api.md#drag_and_drop) | **POST** /api/v2/test-case/tree/bulk/drag-and-drop | dragAndDrop test cases for trees


# **drag_and_drop**
> drag_and_drop(test_case_bulk_drag_and_drop_dto_v2)

dragAndDrop test cases for trees

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_drag_and_drop_dto_v2 import TestCaseBulkDragAndDropDtoV2
from src.client.generated.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = src.client.generated.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with src.client.generated.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = src.client.generated.TestCaseTreeBulkControllerV2Api(api_client)
    test_case_bulk_drag_and_drop_dto_v2 = src.client.generated.TestCaseBulkDragAndDropDtoV2() # TestCaseBulkDragAndDropDtoV2 | 

    try:
        # dragAndDrop test cases for trees
        await api_instance.drag_and_drop(test_case_bulk_drag_and_drop_dto_v2)
    except Exception as e:
        print("Exception when calling TestCaseTreeBulkControllerV2Api->drag_and_drop: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_drag_and_drop_dto_v2** | [**TestCaseBulkDragAndDropDtoV2**](TestCaseBulkDragAndDropDtoV2.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

