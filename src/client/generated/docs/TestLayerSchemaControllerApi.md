# src.client.generated.TestLayerSchemaControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create8**](TestLayerSchemaControllerApi.md#create8) | **POST** /api/testlayerschema | Create a new test layer schema
[**delete8**](TestLayerSchemaControllerApi.md#delete8) | **DELETE** /api/testlayerschema/{id} | Delete test layer schema by id
[**find_all6**](TestLayerSchemaControllerApi.md#find_all6) | **GET** /api/testlayerschema | Find all test layer schemas for given project
[**find_one7**](TestLayerSchemaControllerApi.md#find_one7) | **GET** /api/testlayerschema/{id} | Find test layer schema by id
[**patch8**](TestLayerSchemaControllerApi.md#patch8) | **PATCH** /api/testlayerschema/{id} | Patch test layer schema


# **create8**
> TestLayerSchemaDto create8(test_layer_schema_create_dto)

Create a new test layer schema

### Example


```python
import src.client.generated
from src.client.generated.models.test_layer_schema_create_dto import TestLayerSchemaCreateDto
from src.client.generated.models.test_layer_schema_dto import TestLayerSchemaDto
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
    api_instance = src.client.generated.TestLayerSchemaControllerApi(api_client)
    test_layer_schema_create_dto = src.client.generated.TestLayerSchemaCreateDto() # TestLayerSchemaCreateDto | 

    try:
        # Create a new test layer schema
        api_response = await api_instance.create8(test_layer_schema_create_dto)
        print("The response of TestLayerSchemaControllerApi->create8:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerSchemaControllerApi->create8: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_layer_schema_create_dto** | [**TestLayerSchemaCreateDto**](TestLayerSchemaCreateDto.md)|  | 

### Return type

[**TestLayerSchemaDto**](TestLayerSchemaDto.md)

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

# **delete8**
> delete8(id)

Delete test layer schema by id

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
    api_instance = src.client.generated.TestLayerSchemaControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete test layer schema by id
        await api_instance.delete8(id)
    except Exception as e:
        print("Exception when calling TestLayerSchemaControllerApi->delete8: %s\n" % e)
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

# **find_all6**
> PageTestLayerSchemaDto find_all6(project_id, page=page, size=size, sort=sort)

Find all test layer schemas for given project

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_layer_schema_dto import PageTestLayerSchemaDto
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
    api_instance = src.client.generated.TestLayerSchemaControllerApi(api_client)
    project_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [id,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [id,ASC])

    try:
        # Find all test layer schemas for given project
        api_response = await api_instance.find_all6(project_id, page=page, size=size, sort=sort)
        print("The response of TestLayerSchemaControllerApi->find_all6:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerSchemaControllerApi->find_all6: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [id,ASC]]

### Return type

[**PageTestLayerSchemaDto**](PageTestLayerSchemaDto.md)

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

# **find_one7**
> TestLayerSchemaDto find_one7(id)

Find test layer schema by id

### Example


```python
import src.client.generated
from src.client.generated.models.test_layer_schema_dto import TestLayerSchemaDto
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
    api_instance = src.client.generated.TestLayerSchemaControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find test layer schema by id
        api_response = await api_instance.find_one7(id)
        print("The response of TestLayerSchemaControllerApi->find_one7:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerSchemaControllerApi->find_one7: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestLayerSchemaDto**](TestLayerSchemaDto.md)

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

# **patch8**
> TestLayerSchemaDto patch8(id, test_layer_schema_patch_dto)

Patch test layer schema

### Example


```python
import src.client.generated
from src.client.generated.models.test_layer_schema_dto import TestLayerSchemaDto
from src.client.generated.models.test_layer_schema_patch_dto import TestLayerSchemaPatchDto
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
    api_instance = src.client.generated.TestLayerSchemaControllerApi(api_client)
    id = 56 # int | 
    test_layer_schema_patch_dto = src.client.generated.TestLayerSchemaPatchDto() # TestLayerSchemaPatchDto | 

    try:
        # Patch test layer schema
        api_response = await api_instance.patch8(id, test_layer_schema_patch_dto)
        print("The response of TestLayerSchemaControllerApi->patch8:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerSchemaControllerApi->patch8: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_layer_schema_patch_dto** | [**TestLayerSchemaPatchDto**](TestLayerSchemaPatchDto.md)|  | 

### Return type

[**TestLayerSchemaDto**](TestLayerSchemaDto.md)

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

