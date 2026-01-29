# src.client.generated.CustomFieldControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**count_usage**](CustomFieldControllerApi.md#count_usage) | **GET** /api/cf/count-usage | Count custom fields usage in projects
[**create52**](CustomFieldControllerApi.md#create52) | **POST** /api/cf | 
[**delete43**](CustomFieldControllerApi.md#delete43) | **DELETE** /api/cf/{id} | 
[**find_by_project**](CustomFieldControllerApi.md#find_by_project) | **GET** /api/cf | Deprecated. Use GET /api/project/{projectId}/cf instead
[**find_one37**](CustomFieldControllerApi.md#find_one37) | **GET** /api/cf/{id} | 
[**merge4**](CustomFieldControllerApi.md#merge4) | **POST** /api/cf/merge | 
[**patch48**](CustomFieldControllerApi.md#patch48) | **PATCH** /api/cf/{id} | 
[**set_archived**](CustomFieldControllerApi.md#set_archived) | **POST** /api/cf/{id}/archived | Soft delete custom field
[**suggest22**](CustomFieldControllerApi.md#suggest22) | **GET** /api/cf/suggest | 


# **count_usage**
> List[CustomFieldProjectCountDto] count_usage(id)

Count custom fields usage in projects

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_project_count_dto import CustomFieldProjectCountDto
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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    id = [56] # List[int] | 

    try:
        # Count custom fields usage in projects
        api_response = await api_instance.count_usage(id)
        print("The response of CustomFieldControllerApi->count_usage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->count_usage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**List[int]**](int.md)|  | 

### Return type

[**List[CustomFieldProjectCountDto]**](CustomFieldProjectCountDto.md)

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

# **create52**
> CustomFieldDto create52(custom_field_create_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_create_dto import CustomFieldCreateDto
from src.client.generated.models.custom_field_dto import CustomFieldDto
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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    custom_field_create_dto = src.client.generated.CustomFieldCreateDto() # CustomFieldCreateDto | 

    try:
        api_response = await api_instance.create52(custom_field_create_dto)
        print("The response of CustomFieldControllerApi->create52:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->create52: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_create_dto** | [**CustomFieldCreateDto**](CustomFieldCreateDto.md)|  | 

### Return type

[**CustomFieldDto**](CustomFieldDto.md)

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

# **delete43**
> delete43(id)

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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    id = 56 # int | 

    try:
        await api_instance.delete43(id)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->delete43: %s\n" % e)
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

# **find_by_project**
> PageCustomFieldProjectDto find_by_project(project_id, query=query, page=page, size=size, sort=sort)

Deprecated. Use GET /api/project/{projectId}/cf instead

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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    project_id = 56 # int | 
    query = 'query_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = ["id,ASC"] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to ["id,ASC"])

    try:
        # Deprecated. Use GET /api/project/{projectId}/cf instead
        api_response = await api_instance.find_by_project(project_id, query=query, page=page, size=size, sort=sort)
        print("The response of CustomFieldControllerApi->find_by_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->find_by_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **query** | **str**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [&quot;id,ASC&quot;]]

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

# **find_one37**
> CustomFieldDto find_one37(id)

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_dto import CustomFieldDto
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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    id = 56 # int | 

    try:
        api_response = await api_instance.find_one37(id)
        print("The response of CustomFieldControllerApi->find_one37:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->find_one37: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**CustomFieldDto**](CustomFieldDto.md)

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

# **merge4**
> merge4(custom_field_merge_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_merge_dto import CustomFieldMergeDto
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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    custom_field_merge_dto = src.client.generated.CustomFieldMergeDto() # CustomFieldMergeDto | 

    try:
        await api_instance.merge4(custom_field_merge_dto)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->merge4: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_merge_dto** | [**CustomFieldMergeDto**](CustomFieldMergeDto.md)|  | 

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

# **patch48**
> CustomFieldDto patch48(id, custom_field_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_dto import CustomFieldDto
from src.client.generated.models.custom_field_patch_dto import CustomFieldPatchDto
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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    id = 56 # int | 
    custom_field_patch_dto = src.client.generated.CustomFieldPatchDto() # CustomFieldPatchDto | 

    try:
        api_response = await api_instance.patch48(id, custom_field_patch_dto)
        print("The response of CustomFieldControllerApi->patch48:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->patch48: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **custom_field_patch_dto** | [**CustomFieldPatchDto**](CustomFieldPatchDto.md)|  | 

### Return type

[**CustomFieldDto**](CustomFieldDto.md)

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

# **set_archived**
> CustomFieldDto set_archived(id, archived=archived)

Soft delete custom field

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_dto import CustomFieldDto
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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    id = 56 # int | 
    archived = True # bool |  (optional)

    try:
        # Soft delete custom field
        api_response = await api_instance.set_archived(id, archived=archived)
        print("The response of CustomFieldControllerApi->set_archived:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->set_archived: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **archived** | **bool**|  | [optional] 

### Return type

[**CustomFieldDto**](CustomFieldDto.md)

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

# **suggest22**
> PageIdAndNameOnlyDto suggest22(project_id=project_id, query=query, exclude_project_id=exclude_project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

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
    api_instance = src.client.generated.CustomFieldControllerApi(api_client)
    project_id = 56 # int |  (optional)
    query = 'query_example' # str |  (optional)
    exclude_project_id = [56] # List[int] |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = ["name,ASC"] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to ["name,ASC"])

    try:
        api_response = await api_instance.suggest22(project_id=project_id, query=query, exclude_project_id=exclude_project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of CustomFieldControllerApi->suggest22:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldControllerApi->suggest22: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | [optional] 
 **query** | **str**|  | [optional] 
 **exclude_project_id** | [**List[int]**](int.md)|  | [optional] 
 **id** | [**List[int]**](int.md)|  | [optional] 
 **ignore_id** | [**List[int]**](int.md)|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [&quot;name,ASC&quot;]]

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

