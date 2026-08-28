# src.client.generated.TestResultTreeControllerV2Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_tree_entities**](TestResultTreeControllerV2Api.md#get_tree_entities) | **GET** /api/v2/launch/{launchId}/test-result/tree/entity | Get test results as a tree structure


# **get_tree_entities**
> PageTestResultTreeNodeDto get_tree_entities(launch_id, tree_id, search=search, filter_id=filter_id, path=path, page=page, size=size, sort=sort)

Get test results as a tree structure

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_result_tree_node_dto import PageTestResultTreeNodeDto
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
    api_instance = src.client.generated.TestResultTreeControllerV2Api(api_client)
    launch_id = 56 # int | 
    tree_id = 56 # int | 
    search = 'search_example' # str |  (optional)
    filter_id = 56 # int |  (optional)
    path = [] # List[int] |  (optional) (default to [])
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Get test results as a tree structure
        api_response = await api_instance.get_tree_entities(launch_id, tree_id, search=search, filter_id=filter_id, path=path, page=page, size=size, sort=sort)
        print("The response of TestResultTreeControllerV2Api->get_tree_entities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultTreeControllerV2Api->get_tree_entities: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **launch_id** | **int**|  | 
 **tree_id** | **int**|  | 
 **search** | **str**|  | [optional] 
 **filter_id** | **int**|  | [optional] 
 **path** | [**List[int]**](int.md)|  | [optional] [default to []]
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestResultTreeNodeDto**](PageTestResultTreeNodeDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

