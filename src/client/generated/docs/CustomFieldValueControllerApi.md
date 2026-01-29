# src.client.generated.CustomFieldValueControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create50**](CustomFieldValueControllerApi.md#create50) | **POST** /api/cfv | Deprecated. Use POST /api/project/{projectId}/cfv instead
[**delete41**](CustomFieldValueControllerApi.md#delete41) | **DELETE** /api/cfv/{id} | Delete custom field value by id
[**find_all44**](CustomFieldValueControllerApi.md#find_all44) | **GET** /api/cfv | Find all custom field values
[**find_one35**](CustomFieldValueControllerApi.md#find_one35) | **GET** /api/cfv/{id} | Find custom field value by id
[**merge_project_fields_to_existing_global_value**](CustomFieldValueControllerApi.md#merge_project_fields_to_existing_global_value) | **POST** /api/cfv/merge-to/{toCfvId} | Merge project custom field values into existing global
[**merge_project_fields_to_new_global_value**](CustomFieldValueControllerApi.md#merge_project_fields_to_new_global_value) | **POST** /api/cfv/merge | Merge project custom field values into new global
[**patch46**](CustomFieldValueControllerApi.md#patch46) | **PATCH** /api/cfv/{id} | Patch custom field value
[**rename_custom_field_value**](CustomFieldValueControllerApi.md#rename_custom_field_value) | **POST** /api/cfv/{id}/rename | Deprecated. Use PUT /api/project/{projectId}/cfv/{cvfId}/name instead
[**suggest21**](CustomFieldValueControllerApi.md#suggest21) | **GET** /api/cfv/suggest | Suggest custom field values
[**suggest_v2**](CustomFieldValueControllerApi.md#suggest_v2) | **GET** /api/cfv/suggest/{projectId} | Suggest custom field values


# **create50**
> CustomFieldValueWithCfDto create50(custom_field_value_project_create_dto)

Deprecated. Use POST /api/project/{projectId}/cfv instead

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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    custom_field_value_project_create_dto = src.client.generated.CustomFieldValueProjectCreateDto() # CustomFieldValueProjectCreateDto | 

    try:
        # Deprecated. Use POST /api/project/{projectId}/cfv instead
        api_response = await api_instance.create50(custom_field_value_project_create_dto)
        print("The response of CustomFieldValueControllerApi->create50:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->create50: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **delete41**
> delete41(id, project_id=project_id)

Delete custom field value by id

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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    id = 56 # int | 
    project_id = 56 # int |  (optional)

    try:
        # Delete custom field value by id
        await api_instance.delete41(id, project_id=project_id)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->delete41: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **project_id** | **int**|  | [optional] 

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

# **find_all44**
> PageCustomFieldValueWithTcCountDto find_all44(custom_field_id, project_id=project_id, var_global=var_global, query=query, strict=strict, test_case_search=test_case_search, page=page, size=size, sort=sort)

Find all custom field values

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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    custom_field_id = 56 # int | 
    project_id = 56 # int |  (optional)
    var_global = True # bool |  (optional)
    query = 'query_example' # str |  (optional)
    strict = True # bool |  (optional)
    test_case_search = 'test_case_search_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find all custom field values
        api_response = await api_instance.find_all44(custom_field_id, project_id=project_id, var_global=var_global, query=query, strict=strict, test_case_search=test_case_search, page=page, size=size, sort=sort)
        print("The response of CustomFieldValueControllerApi->find_all44:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->find_all44: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | 
 **project_id** | **int**|  | [optional] 
 **var_global** | **bool**|  | [optional] 
 **query** | **str**|  | [optional] 
 **strict** | **bool**|  | [optional] 
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

# **find_one35**
> CustomFieldValueWithCfDto find_one35(id)

Find custom field value by id

### Example


```python
import src.client.generated
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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find custom field value by id
        api_response = await api_instance.find_one35(id)
        print("The response of CustomFieldValueControllerApi->find_one35:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->find_one35: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**CustomFieldValueWithCfDto**](CustomFieldValueWithCfDto.md)

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

# **merge_project_fields_to_existing_global_value**
> merge_project_fields_to_existing_global_value(to_cfv_id, cfv_merge_to_existing_global_value_dto)

Merge project custom field values into existing global

### Example


```python
import src.client.generated
from src.client.generated.models.cfv_merge_to_existing_global_value_dto import CfvMergeToExistingGlobalValueDto
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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    to_cfv_id = 56 # int | 
    cfv_merge_to_existing_global_value_dto = src.client.generated.CfvMergeToExistingGlobalValueDto() # CfvMergeToExistingGlobalValueDto | 

    try:
        # Merge project custom field values into existing global
        await api_instance.merge_project_fields_to_existing_global_value(to_cfv_id, cfv_merge_to_existing_global_value_dto)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->merge_project_fields_to_existing_global_value: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **to_cfv_id** | **int**|  | 
 **cfv_merge_to_existing_global_value_dto** | [**CfvMergeToExistingGlobalValueDto**](CfvMergeToExistingGlobalValueDto.md)|  | 

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

# **merge_project_fields_to_new_global_value**
> merge_project_fields_to_new_global_value(cfv_merge_to_new_global_value_dto)

Merge project custom field values into new global

### Example


```python
import src.client.generated
from src.client.generated.models.cfv_merge_to_new_global_value_dto import CfvMergeToNewGlobalValueDto
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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    cfv_merge_to_new_global_value_dto = src.client.generated.CfvMergeToNewGlobalValueDto() # CfvMergeToNewGlobalValueDto | 

    try:
        # Merge project custom field values into new global
        await api_instance.merge_project_fields_to_new_global_value(cfv_merge_to_new_global_value_dto)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->merge_project_fields_to_new_global_value: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cfv_merge_to_new_global_value_dto** | [**CfvMergeToNewGlobalValueDto**](CfvMergeToNewGlobalValueDto.md)|  | 

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

# **patch46**
> CustomFieldValueWithCfDto patch46(id, custom_field_value_patch_dto)

Patch custom field value

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_value_patch_dto import CustomFieldValuePatchDto
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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    id = 56 # int | 
    custom_field_value_patch_dto = src.client.generated.CustomFieldValuePatchDto() # CustomFieldValuePatchDto | 

    try:
        # Patch custom field value
        api_response = await api_instance.patch46(id, custom_field_value_patch_dto)
        print("The response of CustomFieldValueControllerApi->patch46:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->patch46: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **custom_field_value_patch_dto** | [**CustomFieldValuePatchDto**](CustomFieldValuePatchDto.md)|  | 

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

# **rename_custom_field_value**
> rename_custom_field_value(id, custom_field_value_project_rename_dto)

Deprecated. Use PUT /api/project/{projectId}/cfv/{cvfId}/name instead

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_value_project_rename_dto import CustomFieldValueProjectRenameDto
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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    id = 56 # int | 
    custom_field_value_project_rename_dto = src.client.generated.CustomFieldValueProjectRenameDto() # CustomFieldValueProjectRenameDto | 

    try:
        # Deprecated. Use PUT /api/project/{projectId}/cfv/{cvfId}/name instead
        await api_instance.rename_custom_field_value(id, custom_field_value_project_rename_dto)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->rename_custom_field_value: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **custom_field_value_project_rename_dto** | [**CustomFieldValueProjectRenameDto**](CustomFieldValueProjectRenameDto.md)|  | 

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
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **suggest21**
> PageIdAndNameOnlyDto suggest21(custom_field_id=custom_field_id, query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

Suggest custom field values

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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    custom_field_id = 56 # int |  (optional)
    query = 'query_example' # str |  (optional)
    project_id = 56 # int |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Suggest custom field values
        api_response = await api_instance.suggest21(custom_field_id=custom_field_id, query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of CustomFieldValueControllerApi->suggest21:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->suggest21: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | [optional] 
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

# **suggest_v2**
> PageIdAndNameOnlyDto suggest_v2(project_id, custom_field_id=custom_field_id, query=query, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

Suggest custom field values

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
    api_instance = src.client.generated.CustomFieldValueControllerApi(api_client)
    project_id = 56 # int | 
    custom_field_id = 56 # int |  (optional)
    query = 'query_example' # str |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Suggest custom field values
        api_response = await api_instance.suggest_v2(project_id, custom_field_id=custom_field_id, query=query, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of CustomFieldValueControllerApi->suggest_v2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldValueControllerApi->suggest_v2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **custom_field_id** | **int**|  | [optional] 
 **query** | **str**|  | [optional] 
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

