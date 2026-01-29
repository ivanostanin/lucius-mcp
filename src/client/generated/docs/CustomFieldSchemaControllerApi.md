# src.client.generated.CustomFieldSchemaControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**count_mappings**](CustomFieldSchemaControllerApi.md#count_mappings) | **GET** /api/cfschema/count-mappings | Count custom fields mappings
[**create51**](CustomFieldSchemaControllerApi.md#create51) | **POST** /api/cfschema | Create a new custom field schema
[**delete42**](CustomFieldSchemaControllerApi.md#delete42) | **DELETE** /api/cfschema/{id} | Delete custom field schema by id
[**find_all45**](CustomFieldSchemaControllerApi.md#find_all45) | **GET** /api/cfschema | Find all custom field schemas for specified project and custom field
[**find_one36**](CustomFieldSchemaControllerApi.md#find_one36) | **GET** /api/cfschema/{id} | Find custom field schema by id
[**patch47**](CustomFieldSchemaControllerApi.md#patch47) | **PATCH** /api/cfschema/{id} | Patch custom field schema


# **count_mappings**
> List[CustomFieldSchemaCountDto] count_mappings(project_id, id)

Count custom fields mappings

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_schema_count_dto import CustomFieldSchemaCountDto
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
    api_instance = src.client.generated.CustomFieldSchemaControllerApi(api_client)
    project_id = 56 # int | 
    id = [56] # List[int] | 

    try:
        # Count custom fields mappings
        api_response = await api_instance.count_mappings(project_id, id)
        print("The response of CustomFieldSchemaControllerApi->count_mappings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldSchemaControllerApi->count_mappings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **id** | [**List[int]**](int.md)|  | 

### Return type

[**List[CustomFieldSchemaCountDto]**](CustomFieldSchemaCountDto.md)

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

# **create51**
> CustomFieldSchemaDto create51(custom_field_schema_create_dto)

Create a new custom field schema

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_schema_create_dto import CustomFieldSchemaCreateDto
from src.client.generated.models.custom_field_schema_dto import CustomFieldSchemaDto
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
    api_instance = src.client.generated.CustomFieldSchemaControllerApi(api_client)
    custom_field_schema_create_dto = src.client.generated.CustomFieldSchemaCreateDto() # CustomFieldSchemaCreateDto | 

    try:
        # Create a new custom field schema
        api_response = await api_instance.create51(custom_field_schema_create_dto)
        print("The response of CustomFieldSchemaControllerApi->create51:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldSchemaControllerApi->create51: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_schema_create_dto** | [**CustomFieldSchemaCreateDto**](CustomFieldSchemaCreateDto.md)|  | 

### Return type

[**CustomFieldSchemaDto**](CustomFieldSchemaDto.md)

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

# **delete42**
> delete42(id)

Delete custom field schema by id

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
    api_instance = src.client.generated.CustomFieldSchemaControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete custom field schema by id
        await api_instance.delete42(id)
    except Exception as e:
        print("Exception when calling CustomFieldSchemaControllerApi->delete42: %s\n" % e)
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

# **find_all45**
> PageCustomFieldSchemaDto find_all45(project_id, custom_field_id=custom_field_id, page=page, size=size, sort=sort)

Find all custom field schemas for specified project and custom field

### Example


```python
import src.client.generated
from src.client.generated.models.page_custom_field_schema_dto import PageCustomFieldSchemaDto
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
    api_instance = src.client.generated.CustomFieldSchemaControllerApi(api_client)
    project_id = 56 # int | 
    custom_field_id = 56 # int |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [id,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [id,ASC])

    try:
        # Find all custom field schemas for specified project and custom field
        api_response = await api_instance.find_all45(project_id, custom_field_id=custom_field_id, page=page, size=size, sort=sort)
        print("The response of CustomFieldSchemaControllerApi->find_all45:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldSchemaControllerApi->find_all45: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **custom_field_id** | **int**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [id,ASC]]

### Return type

[**PageCustomFieldSchemaDto**](PageCustomFieldSchemaDto.md)

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

# **find_one36**
> CustomFieldSchemaDto find_one36(id)

Find custom field schema by id

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_schema_dto import CustomFieldSchemaDto
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
    api_instance = src.client.generated.CustomFieldSchemaControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find custom field schema by id
        api_response = await api_instance.find_one36(id)
        print("The response of CustomFieldSchemaControllerApi->find_one36:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldSchemaControllerApi->find_one36: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**CustomFieldSchemaDto**](CustomFieldSchemaDto.md)

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

# **patch47**
> CustomFieldSchemaDto patch47(id, custom_field_schema_patch_dto)

Patch custom field schema

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_schema_dto import CustomFieldSchemaDto
from src.client.generated.models.custom_field_schema_patch_dto import CustomFieldSchemaPatchDto
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
    api_instance = src.client.generated.CustomFieldSchemaControllerApi(api_client)
    id = 56 # int | 
    custom_field_schema_patch_dto = src.client.generated.CustomFieldSchemaPatchDto() # CustomFieldSchemaPatchDto | 

    try:
        # Patch custom field schema
        api_response = await api_instance.patch47(id, custom_field_schema_patch_dto)
        print("The response of CustomFieldSchemaControllerApi->patch47:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomFieldSchemaControllerApi->patch47: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **custom_field_schema_patch_dto** | [**CustomFieldSchemaPatchDto**](CustomFieldSchemaPatchDto.md)|  | 

### Return type

[**CustomFieldSchemaDto**](CustomFieldSchemaDto.md)

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

