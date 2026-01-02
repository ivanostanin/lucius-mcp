# src.client.generated.LaunchSearchControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**search2**](LaunchSearchControllerApi.md#search2) | **GET** /api/launch/__search | Find all launches by given AQL
[**validate_query2**](LaunchSearchControllerApi.md#validate_query2) | **GET** /api/launch/query/validate | Find all launches by given AQL


# **search2**
> PageLaunchDto search2(project_id, rql, page=page, size=size, sort=sort)

Find all launches by given AQL

### Example


```python
import src.client.generated
from src.client.generated.models.page_launch_dto import PageLaunchDto
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
    api_instance = src.client.generated.LaunchSearchControllerApi(api_client)
    project_id = 56 # int | 
    rql = 'rql_example' # str | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [created_date,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [created_date,DESC])

    try:
        # Find all launches by given AQL
        api_response = await api_instance.search2(project_id, rql, page=page, size=size, sort=sort)
        print("The response of LaunchSearchControllerApi->search2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LaunchSearchControllerApi->search2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **rql** | **str**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [created_date,DESC]]

### Return type

[**PageLaunchDto**](PageLaunchDto.md)

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

# **validate_query2**
> AqlValidateResponseDto validate_query2(project_id, rql)

Find all launches by given AQL

### Example


```python
import src.client.generated
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
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
    api_instance = src.client.generated.LaunchSearchControllerApi(api_client)
    project_id = 56 # int | 
    rql = 'rql_example' # str | 

    try:
        # Find all launches by given AQL
        api_response = await api_instance.validate_query2(project_id, rql)
        print("The response of LaunchSearchControllerApi->validate_query2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LaunchSearchControllerApi->validate_query2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **rql** | **str**|  | 

### Return type

[**AqlValidateResponseDto**](AqlValidateResponseDto.md)

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

