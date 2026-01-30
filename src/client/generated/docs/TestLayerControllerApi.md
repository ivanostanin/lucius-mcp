# src.client.generated.TestLayerControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create9**](TestLayerControllerApi.md#create9) | **POST** /api/testlayer | 
[**delete9**](TestLayerControllerApi.md#delete9) | **DELETE** /api/testlayer/{id} | 
[**find_all7**](TestLayerControllerApi.md#find_all7) | **GET** /api/testlayer | 
[**find_one8**](TestLayerControllerApi.md#find_one8) | **GET** /api/testlayer/{id} | 
[**patch9**](TestLayerControllerApi.md#patch9) | **PATCH** /api/testlayer/{id} | 
[**suggest4**](TestLayerControllerApi.md#suggest4) | **GET** /api/testlayer/suggest | 


# **create9**
> TestLayerDto create9(test_layer_create_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.test_layer_create_dto import TestLayerCreateDto
from src.client.generated.models.test_layer_dto import TestLayerDto
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
    api_instance = src.client.generated.TestLayerControllerApi(api_client)
    test_layer_create_dto = src.client.generated.TestLayerCreateDto() # TestLayerCreateDto | 

    try:
        api_response = await api_instance.create9(test_layer_create_dto)
        print("The response of TestLayerControllerApi->create9:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerControllerApi->create9: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_layer_create_dto** | [**TestLayerCreateDto**](TestLayerCreateDto.md)|  | 

### Return type

[**TestLayerDto**](TestLayerDto.md)

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

# **delete9**
> delete9(id)

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
    api_instance = src.client.generated.TestLayerControllerApi(api_client)
    id = 56 # int | 

    try:
        await api_instance.delete9(id)
    except Exception as e:
        print("Exception when calling TestLayerControllerApi->delete9: %s\n" % e)
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

# **find_all7**
> PageTestLayerDto find_all7(page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_layer_dto import PageTestLayerDto
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
    api_instance = src.client.generated.TestLayerControllerApi(api_client)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [id,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [id,ASC])

    try:
        api_response = await api_instance.find_all7(page=page, size=size, sort=sort)
        print("The response of TestLayerControllerApi->find_all7:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerControllerApi->find_all7: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [id,ASC]]

### Return type

[**PageTestLayerDto**](PageTestLayerDto.md)

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

# **find_one8**
> TestLayerDto find_one8(id)

### Example


```python
import src.client.generated
from src.client.generated.models.test_layer_dto import TestLayerDto
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
    api_instance = src.client.generated.TestLayerControllerApi(api_client)
    id = 56 # int | 

    try:
        api_response = await api_instance.find_one8(id)
        print("The response of TestLayerControllerApi->find_one8:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerControllerApi->find_one8: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestLayerDto**](TestLayerDto.md)

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

# **patch9**
> TestLayerDto patch9(id, test_layer_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.test_layer_dto import TestLayerDto
from src.client.generated.models.test_layer_patch_dto import TestLayerPatchDto
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
    api_instance = src.client.generated.TestLayerControllerApi(api_client)
    id = 56 # int | 
    test_layer_patch_dto = src.client.generated.TestLayerPatchDto() # TestLayerPatchDto | 

    try:
        api_response = await api_instance.patch9(id, test_layer_patch_dto)
        print("The response of TestLayerControllerApi->patch9:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerControllerApi->patch9: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_layer_patch_dto** | [**TestLayerPatchDto**](TestLayerPatchDto.md)|  | 

### Return type

[**TestLayerDto**](TestLayerDto.md)

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

# **suggest4**
> PageIdAndNameOnlyDto suggest4(query=query, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

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
    api_instance = src.client.generated.TestLayerControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.suggest4(query=query, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of TestLayerControllerApi->suggest4:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLayerControllerApi->suggest4: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

