# src.client.generated.TestCaseControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create13**](TestCaseControllerApi.md#create13) | **POST** /api/testcase | Create a new test case
[**delete13**](TestCaseControllerApi.md#delete13) | **DELETE** /api/testcase/{id} | Delete test case by id
[**detach_automation**](TestCaseControllerApi.md#detach_automation) | **POST** /api/testcase/{id}/detachautomation | Detach automation from test case
[**find_all11**](TestCaseControllerApi.md#find_all11) | **GET** /api/testcase | Find all test cases for specified project
[**find_all_deleted**](TestCaseControllerApi.md#find_all_deleted) | **GET** /api/testcase/deleted | Find all deleted test cases for given project
[**find_all_muted**](TestCaseControllerApi.md#find_all_muted) | **GET** /api/testcase/muted | Find all muted test cases for given project
[**find_history1**](TestCaseControllerApi.md#find_history1) | **GET** /api/testcase/{id}/history | Find run history for test case
[**find_history2**](TestCaseControllerApi.md#find_history2) | **GET** /api/testcase/history | Find run history for test case
[**find_one11**](TestCaseControllerApi.md#find_one11) | **GET** /api/testcase/{id} | Find test case by id
[**find_workflow**](TestCaseControllerApi.md#find_workflow) | **GET** /api/testcase/{id}/workflow | Find workflow for test case
[**patch13**](TestCaseControllerApi.md#patch13) | **PATCH** /api/testcase/{id} | 
[**restore**](TestCaseControllerApi.md#restore) | **POST** /api/testcase/{id}/restore | Restore test case by id
[**suggest6**](TestCaseControllerApi.md#suggest6) | **GET** /api/testcase/suggest | Find suggest for test case


# **create13**
> TestCaseDto create13(test_case_create_v2_dto)

Create a new test case

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto
from src.client.generated.models.test_case_dto import TestCaseDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    test_case_create_v2_dto = src.client.generated.TestCaseCreateV2Dto() # TestCaseCreateV2Dto | 

    try:
        # Create a new test case
        api_response = await api_instance.create13(test_case_create_v2_dto)
        print("The response of TestCaseControllerApi->create13:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->create13: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_create_v2_dto** | [**TestCaseCreateV2Dto**](TestCaseCreateV2Dto.md)|  | 

### Return type

[**TestCaseDto**](TestCaseDto.md)

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

# **delete13**
> delete13(id, force=force)

Delete test case by id

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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    id = 56 # int | 
    force = True # bool |  (optional)

    try:
        # Delete test case by id
        await api_instance.delete13(id, force=force)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->delete13: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **force** | **bool**|  | [optional] 

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
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **detach_automation**
> TestCaseDto detach_automation(id, test_case_detach_automation_rq_dto)

Detach automation from test case

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_detach_automation_rq_dto import TestCaseDetachAutomationRqDto
from src.client.generated.models.test_case_dto import TestCaseDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    id = 56 # int | 
    test_case_detach_automation_rq_dto = src.client.generated.TestCaseDetachAutomationRqDto() # TestCaseDetachAutomationRqDto | 

    try:
        # Detach automation from test case
        api_response = await api_instance.detach_automation(id, test_case_detach_automation_rq_dto)
        print("The response of TestCaseControllerApi->detach_automation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->detach_automation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_case_detach_automation_rq_dto** | [**TestCaseDetachAutomationRqDto**](TestCaseDetachAutomationRqDto.md)|  | 

### Return type

[**TestCaseDto**](TestCaseDto.md)

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

# **find_all11**
> PageTestCaseRowDto find_all11(project_id, page=page, size=size, sort=sort)

Find all test cases for specified project

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_row_dto import PageTestCaseRowDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    project_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Find all test cases for specified project
        api_response = await api_instance.find_all11(project_id, page=page, size=size, sort=sort)
        print("The response of TestCaseControllerApi->find_all11:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->find_all11: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [createdDate,DESC]]

### Return type

[**PageTestCaseRowDto**](PageTestCaseRowDto.md)

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

# **find_all_deleted**
> PageTestCaseRowDto find_all_deleted(project_id, page=page, size=size, sort=sort)

Find all deleted test cases for given project

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_row_dto import PageTestCaseRowDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    project_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Find all deleted test cases for given project
        api_response = await api_instance.find_all_deleted(project_id, page=page, size=size, sort=sort)
        print("The response of TestCaseControllerApi->find_all_deleted:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->find_all_deleted: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [createdDate,DESC]]

### Return type

[**PageTestCaseRowDto**](PageTestCaseRowDto.md)

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

# **find_all_muted**
> PageTestCaseRowDto find_all_muted(project_id, page=page, size=size, sort=sort)

Find all muted test cases for given project

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_row_dto import PageTestCaseRowDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    project_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Find all muted test cases for given project
        api_response = await api_instance.find_all_muted(project_id, page=page, size=size, sort=sort)
        print("The response of TestCaseControllerApi->find_all_muted:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->find_all_muted: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [createdDate,DESC]]

### Return type

[**PageTestCaseRowDto**](PageTestCaseRowDto.md)

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

# **find_history1**
> PageTestResultHistoryDto find_history1(id, search=search, page=page, size=size, sort=sort)

Find run history for test case

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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    id = 56 # int | 
    search = 'search_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Find run history for test case
        api_response = await api_instance.find_history1(id, search=search, page=page, size=size, sort=sort)
        print("The response of TestCaseControllerApi->find_history1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->find_history1: %s\n" % e)
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

# **find_history2**
> PageTestResultHistoryDto find_history2(test_case_id, project_id=project_id, launch_id=launch_id, test_result_id=test_result_id, search=search, page=page, size=size, sort=sort)

Find run history for test case

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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    test_case_id = 56 # int | 
    project_id = 56 # int |  (optional)
    launch_id = 56 # int |  (optional)
    test_result_id = 56 # int |  (optional)
    search = 'search_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Find run history for test case
        api_response = await api_instance.find_history2(test_case_id, project_id=project_id, launch_id=launch_id, test_result_id=test_result_id, search=search, page=page, size=size, sort=sort)
        print("The response of TestCaseControllerApi->find_history2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->find_history2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_id** | **int**|  | 
 **project_id** | **int**|  | [optional] 
 **launch_id** | **int**|  | [optional] 
 **test_result_id** | **int**|  | [optional] 
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

# **find_one11**
> TestCaseDto find_one11(id)

Find test case by id

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_dto import TestCaseDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find test case by id
        api_response = await api_instance.find_one11(id)
        print("The response of TestCaseControllerApi->find_one11:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->find_one11: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestCaseDto**](TestCaseDto.md)

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

# **find_workflow**
> WorkflowDto find_workflow(id)

Find workflow for test case

### Example


```python
import src.client.generated
from src.client.generated.models.workflow_dto import WorkflowDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find workflow for test case
        api_response = await api_instance.find_workflow(id)
        print("The response of TestCaseControllerApi->find_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->find_workflow: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**WorkflowDto**](WorkflowDto.md)

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

# **patch13**
> TestCaseDto patch13(id, test_case_patch_v2_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_dto import TestCaseDto
from src.client.generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    id = 56 # int | 
    test_case_patch_v2_dto = src.client.generated.TestCasePatchV2Dto() # TestCasePatchV2Dto | 

    try:
        api_response = await api_instance.patch13(id, test_case_patch_v2_dto)
        print("The response of TestCaseControllerApi->patch13:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->patch13: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_case_patch_v2_dto** | [**TestCasePatchV2Dto**](TestCasePatchV2Dto.md)|  | 

### Return type

[**TestCaseDto**](TestCaseDto.md)

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

# **restore**
> TestCaseDto restore(id)

Restore test case by id

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_dto import TestCaseDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    id = 56 # int | 

    try:
        # Restore test case by id
        api_response = await api_instance.restore(id)
        print("The response of TestCaseControllerApi->restore:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->restore: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestCaseDto**](TestCaseDto.md)

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

# **suggest6**
> PageIdAndNameOnlyDto suggest6(query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

Find suggest for test case

### Example


```python
import src.client.generated
from src.client.generated.models.page_id_and_name_only_dto import PageIdAndNameOnlyDto
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
    api_instance = src.client.generated.TestCaseControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    project_id = 56 # int |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find suggest for test case
        api_response = await api_instance.suggest6(query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of TestCaseControllerApi->suggest6:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseControllerApi->suggest6: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | [optional] 
 **project_id** | **int**|  | [optional] 
 **id** | [**List[int]**](int.md)|  | [optional] 
 **ignore_id** | [**List[int]**](int.md)|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageIdAndNameOnlyDto**](PageIdAndNameOnlyDto.md)

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

