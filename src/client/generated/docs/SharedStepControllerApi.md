# src.client.generated.SharedStepControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**archive**](SharedStepControllerApi.md#archive) | **POST** /api/sharedstep/{id}/archive | Archive ths shared step
[**create19**](SharedStepControllerApi.md#create19) | **POST** /api/sharedstep | Create a new shared step
[**delete18**](SharedStepControllerApi.md#delete18) | **DELETE** /api/sharedstep/{id} | Delete shared step by id
[**find_all16**](SharedStepControllerApi.md#find_all16) | **GET** /api/sharedstep | Find all shared steps for specified project
[**find_one15**](SharedStepControllerApi.md#find_one15) | **GET** /api/sharedstep/{id} | Find shared step by id
[**patch18**](SharedStepControllerApi.md#patch18) | **PATCH** /api/sharedstep/{id} | Patch a specified shared step
[**unarchive**](SharedStepControllerApi.md#unarchive) | **POST** /api/sharedstep/{id}/unarchive | Unarchive ths shared step


# **archive**
> archive(id)

Archive ths shared step

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
    api_instance = src.client.generated.SharedStepControllerApi(api_client)
    id = 56 # int | 

    try:
        # Archive ths shared step
        await api_instance.archive(id)
    except Exception as e:
        print("Exception when calling SharedStepControllerApi->archive: %s\n" % e)
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
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create19**
> SharedStepDto create19(shared_step_create_dto)

Create a new shared step

### Example


```python
import src.client.generated
from src.client.generated.models.shared_step_create_dto import SharedStepCreateDto
from src.client.generated.models.shared_step_dto import SharedStepDto
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
    api_instance = src.client.generated.SharedStepControllerApi(api_client)
    shared_step_create_dto = src.client.generated.SharedStepCreateDto() # SharedStepCreateDto | 

    try:
        # Create a new shared step
        api_response = await api_instance.create19(shared_step_create_dto)
        print("The response of SharedStepControllerApi->create19:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepControllerApi->create19: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shared_step_create_dto** | [**SharedStepCreateDto**](SharedStepCreateDto.md)|  | 

### Return type

[**SharedStepDto**](SharedStepDto.md)

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

# **delete18**
> delete18(id)

Delete shared step by id

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
    api_instance = src.client.generated.SharedStepControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete shared step by id
        await api_instance.delete18(id)
    except Exception as e:
        print("Exception when calling SharedStepControllerApi->delete18: %s\n" % e)
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
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **find_all16**
> PageSharedStepDto find_all16(project_id, search=search, archived=archived, page=page, size=size, sort=sort)

Find all shared steps for specified project

### Example


```python
import src.client.generated
from src.client.generated.models.page_shared_step_dto import PageSharedStepDto
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
    api_instance = src.client.generated.SharedStepControllerApi(api_client)
    project_id = 56 # int | 
    search = 'search_example' # str |  (optional)
    archived = True # bool |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = ["createdDate,DESC"] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to ["createdDate,DESC"])

    try:
        # Find all shared steps for specified project
        api_response = await api_instance.find_all16(project_id, search=search, archived=archived, page=page, size=size, sort=sort)
        print("The response of SharedStepControllerApi->find_all16:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepControllerApi->find_all16: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **search** | **str**|  | [optional] 
 **archived** | **bool**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [&quot;createdDate,DESC&quot;]]

### Return type

[**PageSharedStepDto**](PageSharedStepDto.md)

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

# **find_one15**
> SharedStepDto find_one15(id)

Find shared step by id

### Example


```python
import src.client.generated
from src.client.generated.models.shared_step_dto import SharedStepDto
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
    api_instance = src.client.generated.SharedStepControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find shared step by id
        api_response = await api_instance.find_one15(id)
        print("The response of SharedStepControllerApi->find_one15:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepControllerApi->find_one15: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**SharedStepDto**](SharedStepDto.md)

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

# **patch18**
> SharedStepDto patch18(id, shared_step_patch_dto)

Patch a specified shared step

### Example


```python
import src.client.generated
from src.client.generated.models.shared_step_dto import SharedStepDto
from src.client.generated.models.shared_step_patch_dto import SharedStepPatchDto
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
    api_instance = src.client.generated.SharedStepControllerApi(api_client)
    id = 56 # int | 
    shared_step_patch_dto = src.client.generated.SharedStepPatchDto() # SharedStepPatchDto | 

    try:
        # Patch a specified shared step
        api_response = await api_instance.patch18(id, shared_step_patch_dto)
        print("The response of SharedStepControllerApi->patch18:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepControllerApi->patch18: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **shared_step_patch_dto** | [**SharedStepPatchDto**](SharedStepPatchDto.md)|  | 

### Return type

[**SharedStepDto**](SharedStepDto.md)

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

# **unarchive**
> unarchive(id)

Unarchive ths shared step

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
    api_instance = src.client.generated.SharedStepControllerApi(api_client)
    id = 56 # int | 

    try:
        # Unarchive ths shared step
        await api_instance.unarchive(id)
    except Exception as e:
        print("Exception when calling SharedStepControllerApi->unarchive: %s\n" % e)
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
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

