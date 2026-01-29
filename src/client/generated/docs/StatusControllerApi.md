# src.client.generated.StatusControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create18**](StatusControllerApi.md#create18) | **POST** /api/status | Create a new status
[**delete17**](StatusControllerApi.md#delete17) | **DELETE** /api/status/{id} | Delete status by id
[**find_all15**](StatusControllerApi.md#find_all15) | **GET** /api/status | Find all statuses
[**find_one14**](StatusControllerApi.md#find_one14) | **GET** /api/status/{id} | Find status by id
[**patch17**](StatusControllerApi.md#patch17) | **PATCH** /api/status/{id} | Patch status
[**suggest8**](StatusControllerApi.md#suggest8) | **GET** /api/status/suggest | Suggest statuses


# **create18**
> StatusDto create18(status_create_dto)

Create a new status

### Example


```python
import src.client.generated
from src.client.generated.models.status_create_dto import StatusCreateDto
from src.client.generated.models.status_dto import StatusDto
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
    api_instance = src.client.generated.StatusControllerApi(api_client)
    status_create_dto = src.client.generated.StatusCreateDto() # StatusCreateDto | 

    try:
        # Create a new status
        api_response = await api_instance.create18(status_create_dto)
        print("The response of StatusControllerApi->create18:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusControllerApi->create18: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status_create_dto** | [**StatusCreateDto**](StatusCreateDto.md)|  | 

### Return type

[**StatusDto**](StatusDto.md)

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

# **delete17**
> delete17(id)

Delete status by id

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
    api_instance = src.client.generated.StatusControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete status by id
        await api_instance.delete17(id)
    except Exception as e:
        print("Exception when calling StatusControllerApi->delete17: %s\n" % e)
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

# **find_all15**
> PageStatusDto find_all15(workflow_id=workflow_id, page=page, size=size, sort=sort)

Find all statuses

### Example


```python
import src.client.generated
from src.client.generated.models.page_status_dto import PageStatusDto
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
    api_instance = src.client.generated.StatusControllerApi(api_client)
    workflow_id = 56 # int |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find all statuses
        api_response = await api_instance.find_all15(workflow_id=workflow_id, page=page, size=size, sort=sort)
        print("The response of StatusControllerApi->find_all15:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusControllerApi->find_all15: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **int**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageStatusDto**](PageStatusDto.md)

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

# **find_one14**
> StatusDto find_one14(id)

Find status by id

### Example


```python
import src.client.generated
from src.client.generated.models.status_dto import StatusDto
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
    api_instance = src.client.generated.StatusControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find status by id
        api_response = await api_instance.find_one14(id)
        print("The response of StatusControllerApi->find_one14:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusControllerApi->find_one14: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**StatusDto**](StatusDto.md)

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

# **patch17**
> StatusDto patch17(id, status_patch_dto)

Patch status

### Example


```python
import src.client.generated
from src.client.generated.models.status_dto import StatusDto
from src.client.generated.models.status_patch_dto import StatusPatchDto
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
    api_instance = src.client.generated.StatusControllerApi(api_client)
    id = 56 # int | 
    status_patch_dto = src.client.generated.StatusPatchDto() # StatusPatchDto | 

    try:
        # Patch status
        api_response = await api_instance.patch17(id, status_patch_dto)
        print("The response of StatusControllerApi->patch17:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusControllerApi->patch17: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **status_patch_dto** | [**StatusPatchDto**](StatusPatchDto.md)|  | 

### Return type

[**StatusDto**](StatusDto.md)

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

# **suggest8**
> PageIdAndNameOnlyDto suggest8(query=query, workflow_id=workflow_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

Suggest statuses

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
    api_instance = src.client.generated.StatusControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    workflow_id = 56 # int |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Suggest statuses
        api_response = await api_instance.suggest8(query=query, workflow_id=workflow_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of StatusControllerApi->suggest8:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusControllerApi->suggest8: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | [optional] 
 **workflow_id** | **int**|  | [optional] 
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

