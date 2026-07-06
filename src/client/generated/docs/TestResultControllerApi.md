# src.client.generated.TestResultControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create5**](TestResultControllerApi.md#create5) | **POST** /api/testresult | Create a new test result
[**defects**](TestResultControllerApi.md#defects) | **GET** /api/testresult/defects | Find defects by launch id
[**delete_by_id**](TestResultControllerApi.md#delete_by_id) | **DELETE** /api/testresult/{id} | Delete test result by given id
[**find_all4**](TestResultControllerApi.md#find_all4) | **GET** /api/testresult | Finds all test results by given launch
[**find_execution**](TestResultControllerApi.md#find_execution) | **GET** /api/testresult/{id}/execution | Find all execution for given test result
[**find_history**](TestResultControllerApi.md#find_history) | **GET** /api/testresult/{id}/history | Find all history for given test result
[**find_one5**](TestResultControllerApi.md#find_one5) | **GET** /api/testresult/{id} | 
[**find_retries**](TestResultControllerApi.md#find_retries) | **GET** /api/testresult/{id}/retries | Find all retries for given test result
[**patch5**](TestResultControllerApi.md#patch5) | **PATCH** /api/testresult/{id} | Patches a test result by given id
[**timeline**](TestResultControllerApi.md#timeline) | **GET** /api/testresult/timeline | Find timeline data


# **create5**
> TestResultDto create5(test_result_create_v2_dto)

Create a new test result

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_create_v2_dto import TestResultCreateV2Dto
from src.client.generated.models.test_result_dto import TestResultDto
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    test_result_create_v2_dto = src.client.generated.TestResultCreateV2Dto() # TestResultCreateV2Dto | 

    try:
        # Create a new test result
        api_response = await api_instance.create5(test_result_create_v2_dto)
        print("The response of TestResultControllerApi->create5:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->create5: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_create_v2_dto** | [**TestResultCreateV2Dto**](TestResultCreateV2Dto.md)|  | 

### Return type

[**TestResultDto**](TestResultDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **defects**
> TestResultTree defects(launch_id)

Find defects by launch id

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_tree import TestResultTree
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    launch_id = 56 # int | 

    try:
        # Find defects by launch id
        api_response = await api_instance.defects(launch_id)
        print("The response of TestResultControllerApi->defects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->defects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **launch_id** | **int**|  | 

### Return type

[**TestResultTree**](TestResultTree.md)

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

# **delete_by_id**
> delete_by_id(id)

Delete test result by given id

### Example


```python
import src.client.generated
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete test result by given id
        await api_instance.delete_by_id(id)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->delete_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | No Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **find_all4**
> PageTestResultDto find_all4(launch_id, page=page, size=size, sort=sort)

Finds all test results by given launch

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_result_dto import PageTestResultDto
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    launch_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Finds all test results by given launch
        api_response = await api_instance.find_all4(launch_id, page=page, size=size, sort=sort)
        print("The response of TestResultControllerApi->find_all4:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->find_all4: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **launch_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [createdDate,DESC]]

### Return type

[**PageTestResultDto**](PageTestResultDto.md)

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

# **find_execution**
> TestResultScenarioV2Dto find_execution(id)

Find all execution for given test result

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_scenario_v2_dto import TestResultScenarioV2Dto
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find all execution for given test result
        api_response = await api_instance.find_execution(id)
        print("The response of TestResultControllerApi->find_execution:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->find_execution: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestResultScenarioV2Dto**](TestResultScenarioV2Dto.md)

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

# **find_history**
> PageTestResultHistoryDto find_history(id, search=search, page=page, size=size, sort=sort)

Find all history for given test result

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_result_history_dto import PageTestResultHistoryDto
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    id = 56 # int | 
    search = 'search_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Find all history for given test result
        api_response = await api_instance.find_history(id, search=search, page=page, size=size, sort=sort)
        print("The response of TestResultControllerApi->find_history:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->find_history: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **search** | **str**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [createdDate,DESC]]

### Return type

[**PageTestResultHistoryDto**](PageTestResultHistoryDto.md)

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

# **find_one5**
> TestResultDto find_one5(id)

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_dto import TestResultDto
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    id = 56 # int | 

    try:
        api_response = await api_instance.find_one5(id)
        print("The response of TestResultControllerApi->find_one5:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->find_one5: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestResultDto**](TestResultDto.md)

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

# **find_retries**
> PageTestResultHistoryDto find_retries(id, page=page, size=size, sort=sort)

Find all retries for given test result

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_result_history_dto import PageTestResultHistoryDto
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = ["start,DESC"] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to ["start,DESC"])

    try:
        # Find all retries for given test result
        api_response = await api_instance.find_retries(id, page=page, size=size, sort=sort)
        print("The response of TestResultControllerApi->find_retries:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->find_retries: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [&quot;start,DESC&quot;]]

### Return type

[**PageTestResultHistoryDto**](PageTestResultHistoryDto.md)

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

# **patch5**
> TestResultDto patch5(id, test_result_patch_dto)

Patches a test result by given id

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_dto import TestResultDto
from src.client.generated.models.test_result_patch_dto import TestResultPatchDto
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    id = 56 # int | 
    test_result_patch_dto = src.client.generated.TestResultPatchDto() # TestResultPatchDto | 

    try:
        # Patches a test result by given id
        api_response = await api_instance.patch5(id, test_result_patch_dto)
        print("The response of TestResultControllerApi->patch5:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->patch5: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_result_patch_dto** | [**TestResultPatchDto**](TestResultPatchDto.md)|  | 

### Return type

[**TestResultDto**](TestResultDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **timeline**
> TestResultTree timeline(launch_id)

Find timeline data

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_tree import TestResultTree
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
    api_instance = src.client.generated.TestResultControllerApi(api_client)
    launch_id = 56 # int | 

    try:
        # Find timeline data
        api_response = await api_instance.timeline(launch_id)
        print("The response of TestResultControllerApi->timeline:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultControllerApi->timeline: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **launch_id** | **int**|  | 

### Return type

[**TestResultTree**](TestResultTree.md)

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

