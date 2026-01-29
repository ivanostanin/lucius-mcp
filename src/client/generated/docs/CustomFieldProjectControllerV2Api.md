# src.client.generated.CustomFieldProjectControllerV2Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**find_by_project1**](CustomFieldProjectControllerV2Api.md#find_by_project1) | **GET** /api/project/{projectId}/cf | Find custom fields used in specified project
[**patch24**](CustomFieldProjectControllerV2Api.md#patch24) | **PATCH** /api/project/{projectId}/cf/{cfId} | 


# **find_by_project1**
> PageCustomFieldProjectDto find_by_project1(project_id, query=query, page=page, size=size, sort=sort)

Find custom fields used in specified project

### Example


```python
import src.client.generated
from src.client.generated.models.page_custom_field_project_dto import PageCustomFieldProjectDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerV2Api(api_client)
    project_id = 56 # int | 
    query = 'query_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [id,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [id,ASC])

    try:
        # Find custom fields used in specified project
        api_response = await api_instance.find_by_project1(project_id, query=query, page=page, size=size, sort=sort)
        print("The response of CustomFieldProjectControllerV2Api->find_by_project1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerV2Api->find_by_project1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **query** | **str**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [id,ASC]]

### Return type

[**PageCustomFieldProjectDto**](PageCustomFieldProjectDto.md)

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

# **patch24**
> patch24(project_id, cf_id, custom_field_project_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_project_patch_dto import CustomFieldProjectPatchDto
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
    api_instance = src.client.generated.CustomFieldProjectControllerV2Api(api_client)
    project_id = 56 # int | 
    cf_id = 56 # int | 
    custom_field_project_patch_dto = src.client.generated.CustomFieldProjectPatchDto() # CustomFieldProjectPatchDto | 

    try:
        await api_instance.patch24(project_id, cf_id, custom_field_project_patch_dto)
    except Exception as e:
        print("Exception when calling CustomFieldProjectControllerV2Api->patch24: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **cf_id** | **int**|  | 
 **custom_field_project_patch_dto** | [**CustomFieldProjectPatchDto**](CustomFieldProjectPatchDto.md)|  | 

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

