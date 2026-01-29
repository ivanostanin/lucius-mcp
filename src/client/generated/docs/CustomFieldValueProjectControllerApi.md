# src.client.generated.CustomFieldValueProjectControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create26**](CustomFieldValueProjectControllerApi.md#create26) | **POST** /api/project/{projectId}/cfv | Create a new custom field value for specified project
[**delete47**](CustomFieldValueProjectControllerApi.md#delete47) | **DELETE** /api/project/{projectId}/cfv/{id} | Delete specified custom field value for specified project
[**find_all22**](CustomFieldValueProjectControllerApi.md#find_all22) | **GET** /api/project/{projectId}/cfv | Find all custom field values for specified project
[**merge_custom_fields_to_existing_record**](CustomFieldValueProjectControllerApi.md#merge_custom_fields_to_existing_record) | **POST** /api/project/{projectId}/cfv/merge-to/{toCfvId} | Merge custom field values to existing record by id
[**merge_custom_fields_to_new_record**](CustomFieldValueProjectControllerApi.md#merge_custom_fields_to_new_record) | **POST** /api/project/{projectId}/cfv/merge | Merge custom field values to new record
[**patch23**](CustomFieldValueProjectControllerApi.md#patch23) | **PATCH** /api/project/{projectId}/cfv/{cfvId} | Patch specified custom field value, test results won&#39;t be affected


# **create26**
> CustomFieldValueWithCfDto create26(project_id, custom_field_value_project_create_dto)

Create a new custom field value for specified project

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_value_project_create_dto import CustomFieldValueProjectCreateDto
from src.client.generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
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
    api_instance = src.client.generated.CustomFieldValueProjectControllerApi(api_client)
    project_id = 56 # int | 
    custom_field_value_project_create_dto = src.client.generated.CustomFieldValueProjectCreateDto() # CustomFieldValueProjectCreateDto | 

    try:
        # Create a new custom field value for specified project
        api_response = await api_instance.create26(project_id, custom_field_value_project_create_dto)
        print("The response of CustomFieldValueProjectControllerApi->create26:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueProjectControllerApi->create26: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **custom_field_value_project_create_dto** | [**CustomFieldValueProjectCreateDto**](CustomFieldValueProjectCreateDto.md)|  | 

### Return type

[**CustomFieldValueWithCfDto**](CustomFieldValueWithCfDto.md)

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

# **delete47**
> delete47(project_id, id)

Delete specified custom field value for specified project

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
    api_instance = src.client.generated.CustomFieldValueProjectControllerApi(api_client)
    project_id = 56 # int | 
    id = 56 # int | 

    try:
        # Delete specified custom field value for specified project
        await api_instance.delete47(project_id, id)
    except Exception as e:
        print("Exception when calling CustomFieldValueProjectControllerApi->delete47: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
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

# **find_all22**
> PageCustomFieldValueWithTcCountDto find_all22(project_id, custom_field_id, query=query, var_global=var_global, test_case_search=test_case_search, page=page, size=size, sort=sort)

Find all custom field values for specified project

### Example


```python
import src.client.generated
from src.client.generated.models.page_custom_field_value_with_tc_count_dto import PageCustomFieldValueWithTcCountDto
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
    api_instance = src.client.generated.CustomFieldValueProjectControllerApi(api_client)
    project_id = 56 # int | 
    custom_field_id = 56 # int | 
    query = 'query_example' # str |  (optional)
    var_global = True # bool |  (optional)
    test_case_search = 'test_case_search_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find all custom field values for specified project
        api_response = await api_instance.find_all22(project_id, custom_field_id, query=query, var_global=var_global, test_case_search=test_case_search, page=page, size=size, sort=sort)
        print("The response of CustomFieldValueProjectControllerApi->find_all22:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueProjectControllerApi->find_all22: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **custom_field_id** | **int**|  | 
 **query** | **str**|  | [optional] 
 **var_global** | **bool**|  | [optional] 
 **test_case_search** | **str**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageCustomFieldValueWithTcCountDto**](PageCustomFieldValueWithTcCountDto.md)

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

# **merge_custom_fields_to_existing_record**
> merge_custom_fields_to_existing_record(project_id, to_cfv_id, custom_field_value_project_merge_by_id_dto)

Merge custom field values to existing record by id

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_value_project_merge_by_id_dto import CustomFieldValueProjectMergeByIdDto
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
    api_instance = src.client.generated.CustomFieldValueProjectControllerApi(api_client)
    project_id = 56 # int | 
    to_cfv_id = 56 # int | 
    custom_field_value_project_merge_by_id_dto = src.client.generated.CustomFieldValueProjectMergeByIdDto() # CustomFieldValueProjectMergeByIdDto | 

    try:
        # Merge custom field values to existing record by id
        await api_instance.merge_custom_fields_to_existing_record(project_id, to_cfv_id, custom_field_value_project_merge_by_id_dto)
    except Exception as e:
        print("Exception when calling CustomFieldValueProjectControllerApi->merge_custom_fields_to_existing_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **to_cfv_id** | **int**|  | 
 **custom_field_value_project_merge_by_id_dto** | [**CustomFieldValueProjectMergeByIdDto**](CustomFieldValueProjectMergeByIdDto.md)|  | 

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

# **merge_custom_fields_to_new_record**
> merge_custom_fields_to_new_record(project_id, custom_field_value_project_merge_by_name_dto)

Merge custom field values to new record

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_value_project_merge_by_name_dto import CustomFieldValueProjectMergeByNameDto
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
    api_instance = src.client.generated.CustomFieldValueProjectControllerApi(api_client)
    project_id = 56 # int | 
    custom_field_value_project_merge_by_name_dto = src.client.generated.CustomFieldValueProjectMergeByNameDto() # CustomFieldValueProjectMergeByNameDto | 

    try:
        # Merge custom field values to new record
        await api_instance.merge_custom_fields_to_new_record(project_id, custom_field_value_project_merge_by_name_dto)
    except Exception as e:
        print("Exception when calling CustomFieldValueProjectControllerApi->merge_custom_fields_to_new_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **custom_field_value_project_merge_by_name_dto** | [**CustomFieldValueProjectMergeByNameDto**](CustomFieldValueProjectMergeByNameDto.md)|  | 

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

# **patch23**
> patch23(project_id, cfv_id, custom_field_value_project_patch_dto)

Patch specified custom field value, test results won't be affected

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_value_project_patch_dto import CustomFieldValueProjectPatchDto
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
    api_instance = src.client.generated.CustomFieldValueProjectControllerApi(api_client)
    project_id = 56 # int | 
    cfv_id = 56 # int | 
    custom_field_value_project_patch_dto = src.client.generated.CustomFieldValueProjectPatchDto() # CustomFieldValueProjectPatchDto | 

    try:
        # Patch specified custom field value, test results won't be affected
        await api_instance.patch23(project_id, cfv_id, custom_field_value_project_patch_dto)
    except Exception as e:
        print("Exception when calling CustomFieldValueProjectControllerApi->patch23: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **cfv_id** | **int**|  | 
 **custom_field_value_project_patch_dto** | [**CustomFieldValueProjectPatchDto**](CustomFieldValueProjectPatchDto.md)|  | 

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

