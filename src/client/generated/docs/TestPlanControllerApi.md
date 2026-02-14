# src.client.generated.TestPlanControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**assign2**](TestPlanControllerApi.md#assign2) | **POST** /api/testplan/{id}/assign | Assign test plan test cases to user
[**create7**](TestPlanControllerApi.md#create7) | **POST** /api/testplan | Create a new test plan
[**delete7**](TestPlanControllerApi.md#delete7) | **DELETE** /api/testplan/{id} | Delete test plan by given id
[**find_all_by_project**](TestPlanControllerApi.md#find_all_by_project) | **GET** /api/testplan | Find all test plans for given project
[**find_one6**](TestPlanControllerApi.md#find_one6) | **GET** /api/testplan/{id} | Find test plan by id
[**get_diff**](TestPlanControllerApi.md#get_diff) | **GET** /api/testplan/{id}/diff | Get test plan test cases changes
[**get_groups2**](TestPlanControllerApi.md#get_groups2) | **GET** /api/testplan/{id}/tree/group | Find tree groups for node
[**get_jobs**](TestPlanControllerApi.md#get_jobs) | **GET** /api/testplan/{id}/job | Get test plan jobs statistic
[**get_leafs1**](TestPlanControllerApi.md#get_leafs1) | **GET** /api/testplan/{id}/tree/leaf | Find tree leafs for node
[**get_members2**](TestPlanControllerApi.md#get_members2) | **GET** /api/testplan/{id}/member | Get test plan members statistic
[**patch7**](TestPlanControllerApi.md#patch7) | **PATCH** /api/testplan/{id} | Patch test plan
[**reset_jobs**](TestPlanControllerApi.md#reset_jobs) | **POST** /api/testplan/{id}/resetjob | Reset test plan
[**run3**](TestPlanControllerApi.md#run3) | **POST** /api/testplan/{id}/run | Run test plan by given id
[**set_job_parameters**](TestPlanControllerApi.md#set_job_parameters) | **POST** /api/testplan/{id}/jobparameter | Configure test plan job parameters
[**suggest3**](TestPlanControllerApi.md#suggest3) | **GET** /api/testplan/suggest | Suggest for test plans
[**sync**](TestPlanControllerApi.md#sync) | **POST** /api/testplan/{id}/sync | Sync test plan


# **assign2**
> assign2(id, test_plan_assign_dto)

Assign test plan test cases to user

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_assign_dto import TestPlanAssignDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 
    test_plan_assign_dto = src.client.generated.TestPlanAssignDto() # TestPlanAssignDto | 

    try:
        # Assign test plan test cases to user
        await api_instance.assign2(id, test_plan_assign_dto)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->assign2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_plan_assign_dto** | [**TestPlanAssignDto**](TestPlanAssignDto.md)|  | 

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
**204** | No Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create7**
> TestPlanDto create7(test_plan_create_dto)

Create a new test plan

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_create_dto import TestPlanCreateDto
from src.client.generated.models.test_plan_dto import TestPlanDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    test_plan_create_dto = src.client.generated.TestPlanCreateDto() # TestPlanCreateDto | 

    try:
        # Create a new test plan
        api_response = await api_instance.create7(test_plan_create_dto)
        print("The response of TestPlanControllerApi->create7:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->create7: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_plan_create_dto** | [**TestPlanCreateDto**](TestPlanCreateDto.md)|  | 

### Return type

[**TestPlanDto**](TestPlanDto.md)

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

# **delete7**
> delete7(id)

Delete test plan by given id

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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete test plan by given id
        await api_instance.delete7(id)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->delete7: %s\n" % e)
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

# **find_all_by_project**
> PageTestPlanDto find_all_by_project(project_id, name=name, tree_id=tree_id, page=page, size=size, sort=sort)

Find all test plans for given project

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_plan_dto import PageTestPlanDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    project_id = 56 # int | 
    name = 'name_example' # str |  (optional)
    tree_id = 56 # int |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find all test plans for given project
        api_response = await api_instance.find_all_by_project(project_id, name=name, tree_id=tree_id, page=page, size=size, sort=sort)
        print("The response of TestPlanControllerApi->find_all_by_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->find_all_by_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **name** | **str**|  | [optional] 
 **tree_id** | **int**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestPlanDto**](PageTestPlanDto.md)

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

# **find_one6**
> TestPlanDto find_one6(id)

Find test plan by id

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_dto import TestPlanDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find test plan by id
        api_response = await api_instance.find_one6(id)
        print("The response of TestPlanControllerApi->find_one6:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->find_one6: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestPlanDto**](TestPlanDto.md)

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

# **get_diff**
> TestPlanDiffDto get_diff(id)

Get test plan test cases changes

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_diff_dto import TestPlanDiffDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 

    try:
        # Get test plan test cases changes
        api_response = await api_instance.get_diff(id)
        print("The response of TestPlanControllerApi->get_diff:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->get_diff: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestPlanDiffDto**](TestPlanDiffDto.md)

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

# **get_groups2**
> PageTestCaseTreeGroupDto get_groups2(id, tree_id=tree_id, path=path, username=username, job_id=job_id, manual=manual, page=page, size=size, sort=sort)

Find tree groups for node

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_tree_group_dto import PageTestCaseTreeGroupDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 
    tree_id = 56 # int |  (optional)
    path = [] # List[int] |  (optional) (default to [])
    username = 'username_example' # str |  (optional)
    job_id = 56 # int |  (optional)
    manual = True # bool |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find tree groups for node
        api_response = await api_instance.get_groups2(id, tree_id=tree_id, path=path, username=username, job_id=job_id, manual=manual, page=page, size=size, sort=sort)
        print("The response of TestPlanControllerApi->get_groups2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->get_groups2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **tree_id** | **int**|  | [optional] 
 **path** | [**List[int]**](int.md)|  | [optional] [default to []]
 **username** | **str**|  | [optional] 
 **job_id** | **int**|  | [optional] 
 **manual** | **bool**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestCaseTreeGroupDto**](PageTestCaseTreeGroupDto.md)

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

# **get_jobs**
> List[TestPlanJobStatDto] get_jobs(id)

Get test plan jobs statistic

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_job_stat_dto import TestPlanJobStatDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 

    try:
        # Get test plan jobs statistic
        api_response = await api_instance.get_jobs(id)
        print("The response of TestPlanControllerApi->get_jobs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->get_jobs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**List[TestPlanJobStatDto]**](TestPlanJobStatDto.md)

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

# **get_leafs1**
> PageTestCaseTreeLeafDto get_leafs1(id, tree_id=tree_id, path=path, username=username, job_id=job_id, manual=manual, page=page, size=size, sort=sort)

Find tree leafs for node

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_tree_leaf_dto import PageTestCaseTreeLeafDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 
    tree_id = 56 # int |  (optional)
    path = [] # List[int] |  (optional) (default to [])
    username = 'username_example' # str |  (optional)
    job_id = 56 # int |  (optional)
    manual = True # bool |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find tree leafs for node
        api_response = await api_instance.get_leafs1(id, tree_id=tree_id, path=path, username=username, job_id=job_id, manual=manual, page=page, size=size, sort=sort)
        print("The response of TestPlanControllerApi->get_leafs1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->get_leafs1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **tree_id** | **int**|  | [optional] 
 **path** | [**List[int]**](int.md)|  | [optional] [default to []]
 **username** | **str**|  | [optional] 
 **job_id** | **int**|  | [optional] 
 **manual** | **bool**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestCaseTreeLeafDto**](PageTestCaseTreeLeafDto.md)

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

# **get_members2**
> List[TestPlanMemberStatDto] get_members2(id)

Get test plan members statistic

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_member_stat_dto import TestPlanMemberStatDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 

    try:
        # Get test plan members statistic
        api_response = await api_instance.get_members2(id)
        print("The response of TestPlanControllerApi->get_members2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->get_members2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**List[TestPlanMemberStatDto]**](TestPlanMemberStatDto.md)

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

# **patch7**
> TestPlanDto patch7(id, test_plan_patch_dto)

Patch test plan

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_dto import TestPlanDto
from src.client.generated.models.test_plan_patch_dto import TestPlanPatchDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 
    test_plan_patch_dto = src.client.generated.TestPlanPatchDto() # TestPlanPatchDto | 

    try:
        # Patch test plan
        api_response = await api_instance.patch7(id, test_plan_patch_dto)
        print("The response of TestPlanControllerApi->patch7:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->patch7: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_plan_patch_dto** | [**TestPlanPatchDto**](TestPlanPatchDto.md)|  | 

### Return type

[**TestPlanDto**](TestPlanDto.md)

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

# **reset_jobs**
> TestPlanDto reset_jobs(id)

Reset test plan

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_dto import TestPlanDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 

    try:
        # Reset test plan
        api_response = await api_instance.reset_jobs(id)
        print("The response of TestPlanControllerApi->reset_jobs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->reset_jobs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestPlanDto**](TestPlanDto.md)

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

# **run3**
> LaunchDto run3(id, test_plan_run_request_dto)

Run test plan by given id

### Example


```python
import src.client.generated
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.test_plan_run_request_dto import TestPlanRunRequestDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 
    test_plan_run_request_dto = src.client.generated.TestPlanRunRequestDto() # TestPlanRunRequestDto | 

    try:
        # Run test plan by given id
        api_response = await api_instance.run3(id, test_plan_run_request_dto)
        print("The response of TestPlanControllerApi->run3:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->run3: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_plan_run_request_dto** | [**TestPlanRunRequestDto**](TestPlanRunRequestDto.md)|  | 

### Return type

[**LaunchDto**](LaunchDto.md)

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

# **set_job_parameters**
> set_job_parameters(id, test_plan_job_parameters_dto)

Configure test plan job parameters

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_job_parameters_dto import TestPlanJobParametersDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 
    test_plan_job_parameters_dto = src.client.generated.TestPlanJobParametersDto() # TestPlanJobParametersDto | 

    try:
        # Configure test plan job parameters
        await api_instance.set_job_parameters(id, test_plan_job_parameters_dto)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->set_job_parameters: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_plan_job_parameters_dto** | [**TestPlanJobParametersDto**](TestPlanJobParametersDto.md)|  | 

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
**204** | No Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **suggest3**
> PageTestPlanRowDto suggest3(query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

Suggest for test plans

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_plan_row_dto import PageTestPlanRowDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    project_id = 56 # int |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Suggest for test plans
        api_response = await api_instance.suggest3(query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of TestPlanControllerApi->suggest3:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->suggest3: %s\n" % e)
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

[**PageTestPlanRowDto**](PageTestPlanRowDto.md)

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

# **sync**
> TestPlanDto sync(id)

Sync test plan

### Example


```python
import src.client.generated
from src.client.generated.models.test_plan_dto import TestPlanDto
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
    api_instance = src.client.generated.TestPlanControllerApi(api_client)
    id = 56 # int | 

    try:
        # Sync test plan
        api_response = await api_instance.sync(id)
        print("The response of TestPlanControllerApi->sync:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestPlanControllerApi->sync: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestPlanDto**](TestPlanDto.md)

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

