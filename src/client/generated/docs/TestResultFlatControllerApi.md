# src.client.generated.TestResultFlatControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_test_cases1**](TestResultFlatControllerApi.md#get_test_cases1) | **GET** /api/v2/launch/{launchId}/test-result/flat | Get test results as a flat structure


# **get_test_cases1**
> PageTestResultFlatDto get_test_cases1(launch_id, search=search, filter_id=filter_id, page=page, size=size, sort=sort)

Get test results as a flat structure

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_result_flat_dto import PageTestResultFlatDto
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
    api_instance = src.client.generated.TestResultFlatControllerApi(api_client)
    launch_id = 56 # int | 
    search = 'search_example' # str |  (optional)
    filter_id = 56 # int |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 100 # int | The size of the page to be returned (optional) (default to 100)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Get test results as a flat structure
        api_response = await api_instance.get_test_cases1(launch_id, search=search, filter_id=filter_id, page=page, size=size, sort=sort)
        print("The response of TestResultFlatControllerApi->get_test_cases1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultFlatControllerApi->get_test_cases1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **launch_id** | **int**|  | 
 **search** | **str**|  | [optional] 
 **filter_id** | **int**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 100]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestResultFlatDto**](PageTestResultFlatDto.md)

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

