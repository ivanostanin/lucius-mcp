# src.client.generated.TestCaseSearchControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**search1**](TestCaseSearchControllerApi.md#search1) | **GET** /api/testcase/__search | Find all test cases by given AQL
[**validate_query1**](TestCaseSearchControllerApi.md#validate_query1) | **GET** /api/testcase/query/validate | Find all test cases by given AQL


# **search1**
> PageTestCaseDto search1(project_id, rql, deleted=deleted, page=page, size=size, sort=sort)

Find all test cases by given AQL

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_dto import PageTestCaseDto
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
    api_instance = src.client.generated.TestCaseSearchControllerApi(api_client)
    project_id = 56 # int | 
    rql = 'rql_example' # str | 
    deleted = False # bool |  (optional) (default to False)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = ["id,DESC"] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to ["id,DESC"])

    try:
        # Find all test cases by given AQL
        api_response = await api_instance.search1(project_id, rql, deleted=deleted, page=page, size=size, sort=sort)
        print("The response of TestCaseSearchControllerApi->search1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseSearchControllerApi->search1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **rql** | **str**|  | 
 **deleted** | **bool**|  | [optional] [default to False]
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [&quot;id,DESC&quot;]]

### Return type

[**PageTestCaseDto**](PageTestCaseDto.md)

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

# **validate_query1**
> AqlValidateResponseDto validate_query1(project_id, rql, deleted=deleted)

Find all test cases by given AQL

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
    api_instance = src.client.generated.TestCaseSearchControllerApi(api_client)
    project_id = 56 # int | 
    rql = 'rql_example' # str | 
    deleted = False # bool |  (optional) (default to False)

    try:
        # Find all test cases by given AQL
        api_response = await api_instance.validate_query1(project_id, rql, deleted=deleted)
        print("The response of TestCaseSearchControllerApi->validate_query1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseSearchControllerApi->validate_query1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **rql** | **str**|  | 
 **deleted** | **bool**|  | [optional] [default to False]

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

