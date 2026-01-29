# src.client.generated.CustomFieldProjectControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add2**](CustomFieldProjectControllerApi.md#add2) | **POST** /api/cfproject/add | Add custom field to projects
[**add_to_project**](CustomFieldProjectControllerApi.md#add_to_project) | **POST** /api/cfproject/add-to-project | Add custom fields to project
[**cf_delta1**](CustomFieldProjectControllerApi.md#cf_delta1) | **POST** /api/cfproject/delta | Find missing custom fields
[**find_one45**](CustomFieldProjectControllerApi.md#find_one45) | **GET** /api/cfproject | 
[**find_projects_by_custom_field**](CustomFieldProjectControllerApi.md#find_projects_by_custom_field) | **GET** /api/cfproject/in-projects | Find projects that use specified custom field
[**remove4**](CustomFieldProjectControllerApi.md#remove4) | **DELETE** /api/cfproject/remove | Remove custom field from project
[**set_default**](CustomFieldProjectControllerApi.md#set_default) | **POST** /api/cfproject/default | Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead
[**set_required**](CustomFieldProjectControllerApi.md#set_required) | **POST** /api/cfproject/required | Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead


# **add2**
> add2(custom_field_id, list_selection_dto)

Add custom field to projects

### Example


```python
import src.client.generated
from src.client.generated.models.list_selection_dto import ListSelectionDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    custom_field_id = 56 # int | 
    list_selection_dto = src.client.generated.ListSelectionDto() # ListSelectionDto | 

    try:
        # Add custom field to projects
        await api_instance.add2(custom_field_id, list_selection_dto)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->add2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | 
 **list_selection_dto** | [**ListSelectionDto**](ListSelectionDto.md)|  | 

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

# **add_to_project**
> add_to_project(project_id, list_selection_dto)

Add custom fields to project

### Example


```python
import src.client.generated
from src.client.generated.models.list_selection_dto import ListSelectionDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    project_id = 56 # int | 
    list_selection_dto = src.client.generated.ListSelectionDto() # ListSelectionDto | 

    try:
        # Add custom fields to project
        await api_instance.add_to_project(project_id, list_selection_dto)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->add_to_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **list_selection_dto** | [**ListSelectionDto**](ListSelectionDto.md)|  | 

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

# **cf_delta1**
> List[IdAndNameOnlyDto] cf_delta1(to_project_id, test_case_id=test_case_id, test_case_tree_selection_dto=test_case_tree_selection_dto)

Find missing custom fields

### Example


```python
import src.client.generated
from src.client.generated.models.id_and_name_only_dto import IdAndNameOnlyDto
from src.client.generated.models.test_case_tree_selection_dto import TestCaseTreeSelectionDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    to_project_id = 56 # int | 
    test_case_id = [56] # List[int] |  (optional)
    test_case_tree_selection_dto = src.client.generated.TestCaseTreeSelectionDto() # TestCaseTreeSelectionDto |  (optional)

    try:
        # Find missing custom fields
        api_response = await api_instance.cf_delta1(to_project_id, test_case_id=test_case_id, test_case_tree_selection_dto=test_case_tree_selection_dto)
        print("The response of CustomFieldProjectControllerApi->cf_delta1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->cf_delta1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **to_project_id** | **int**|  | 
 **test_case_id** | [**List[int]**](int.md)|  | [optional] 
 **test_case_tree_selection_dto** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md)|  | [optional] 

### Return type

[**List[IdAndNameOnlyDto]**](IdAndNameOnlyDto.md)

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

# **find_one45**
> CustomFieldProjectDto find_one45(custom_field_id, project_id)

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_project_dto import CustomFieldProjectDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    custom_field_id = 56 # int | 
    project_id = 56 # int | 

    try:
        api_response = await api_instance.find_one45(custom_field_id, project_id)
        print("The response of CustomFieldProjectControllerApi->find_one45:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->find_one45: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | 
 **project_id** | **int**|  | 

### Return type

[**CustomFieldProjectDto**](CustomFieldProjectDto.md)

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

# **find_projects_by_custom_field**
> PageProjectCustomFieldDto find_projects_by_custom_field(custom_field_id, query=query, page=page, size=size, sort=sort)

Find projects that use specified custom field

### Example


```python
import src.client.generated
from src.client.generated.models.page_project_custom_field_dto import PageProjectCustomFieldDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    custom_field_id = 56 # int | 
    query = 'query_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find projects that use specified custom field
        api_response = await api_instance.find_projects_by_custom_field(custom_field_id, query=query, page=page, size=size, sort=sort)
        print("The response of CustomFieldProjectControllerApi->find_projects_by_custom_field:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->find_projects_by_custom_field: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | 
 **query** | **str**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageProjectCustomFieldDto**](PageProjectCustomFieldDto.md)

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

# **remove4**
> remove4(custom_field_id, project_id)

Remove custom field from project

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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    custom_field_id = 56 # int | 
    project_id = 56 # int | 

    try:
        # Remove custom field from project
        await api_instance.remove4(custom_field_id, project_id)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->remove4: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | 
 **project_id** | **int**|  | 

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

# **set_default**
> set_default(default_custom_field_value_dto)

Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead

### Example


```python
import src.client.generated
from src.client.generated.models.default_custom_field_value_dto import DefaultCustomFieldValueDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    default_custom_field_value_dto = src.client.generated.DefaultCustomFieldValueDto() # DefaultCustomFieldValueDto | 

    try:
        # Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead
        await api_instance.set_default(default_custom_field_value_dto)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->set_default: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **default_custom_field_value_dto** | [**DefaultCustomFieldValueDto**](DefaultCustomFieldValueDto.md)|  | 

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

# **set_required**
> set_required(custom_field_id, project_id, required)

Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead

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
    api_instance = src.client.generated.CustomFieldProjectControllerApi(api_client)
    custom_field_id = 56 # int | 
    project_id = 56 # int | 
    required = True # bool | 

    try:
        # Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead
        await api_instance.set_required(custom_field_id, project_id, required)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerApi->set_required: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | 
 **project_id** | **int**|  | 
 **required** | **bool**|  | 

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

