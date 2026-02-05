# src.client.generated.IntegrationControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create37**](IntegrationControllerApi.md#create37) | **POST** /api/integration | 
[**create_project_integration**](IntegrationControllerApi.md#create_project_integration) | **POST** /api/integration/project | 
[**delete_by_id3**](IntegrationControllerApi.md#delete_by_id3) | **DELETE** /api/integration/{id} | 
[**delete_project_integration**](IntegrationControllerApi.md#delete_project_integration) | **DELETE** /api/integration/{integrationId}/project/{projectId} | 
[**find_one_by_id**](IntegrationControllerApi.md#find_one_by_id) | **GET** /api/integration/{id} | 
[**find_project_integration_by_id**](IntegrationControllerApi.md#find_project_integration_by_id) | **GET** /api/integration/{integrationId}/project/{projectId} | 
[**get_available_integrations**](IntegrationControllerApi.md#get_available_integrations) | **GET** /api/integration/available | 
[**get_global_fields**](IntegrationControllerApi.md#get_global_fields) | **GET** /api/integration/globalfields | 
[**get_integration_projects**](IntegrationControllerApi.md#get_integration_projects) | **GET** /api/integration/{id}/project | 
[**get_integrations**](IntegrationControllerApi.md#get_integrations) | **GET** /api/integration | 
[**get_project_available_integrations**](IntegrationControllerApi.md#get_project_available_integrations) | **GET** /api/integration/project/{projectId}/available | 
[**get_project_integration_fields**](IntegrationControllerApi.md#get_project_integration_fields) | **GET** /api/integration/projectfields | 
[**get_project_integrations**](IntegrationControllerApi.md#get_project_integrations) | **GET** /api/integration/project/{projectId} | 
[**patch34**](IntegrationControllerApi.md#patch34) | **PATCH** /api/integration/{id} | 
[**patch_project_integration**](IntegrationControllerApi.md#patch_project_integration) | **PATCH** /api/integration/{integrationId}/project/{projectId} | 
[**suggest15**](IntegrationControllerApi.md#suggest15) | **GET** /api/integration/suggest | Suggest integrations
[**validate1**](IntegrationControllerApi.md#validate1) | **POST** /api/integration/validate | 
[**validate2**](IntegrationControllerApi.md#validate2) | **POST** /api/integration/project/validate | 


# **create37**
> IntegrationDto create37(integration_create_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.integration_create_dto import IntegrationCreateDto
from src.client.generated.models.integration_dto import IntegrationDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    integration_create_dto = src.client.generated.IntegrationCreateDto() # IntegrationCreateDto | 

    try:
        api_response = await api_instance.create37(integration_create_dto)
        print("The response of IntegrationControllerApi->create37:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->create37: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_create_dto** | [**IntegrationCreateDto**](IntegrationCreateDto.md)|  | 

### Return type

[**IntegrationDto**](IntegrationDto.md)

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

# **create_project_integration**
> ProjectIntegrationDto create_project_integration(project_integration_create_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.project_integration_create_dto import ProjectIntegrationCreateDto
from src.client.generated.models.project_integration_dto import ProjectIntegrationDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    project_integration_create_dto = src.client.generated.ProjectIntegrationCreateDto() # ProjectIntegrationCreateDto | 

    try:
        api_response = await api_instance.create_project_integration(project_integration_create_dto)
        print("The response of IntegrationControllerApi->create_project_integration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->create_project_integration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_integration_create_dto** | [**ProjectIntegrationCreateDto**](ProjectIntegrationCreateDto.md)|  | 

### Return type

[**ProjectIntegrationDto**](ProjectIntegrationDto.md)

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

# **delete_by_id3**
> delete_by_id3(id)

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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    id = 56 # int | 

    try:
        await api_instance.delete_by_id3(id)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->delete_by_id3: %s\n" % e)
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

# **delete_project_integration**
> delete_project_integration(integration_id, project_id)

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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    integration_id = 56 # int | 
    project_id = 56 # int | 

    try:
        await api_instance.delete_project_integration(integration_id, project_id)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->delete_project_integration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_id** | **int**|  | 
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
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **find_one_by_id**
> IntegrationDto find_one_by_id(id)

### Example


```python
import src.client.generated
from src.client.generated.models.integration_dto import IntegrationDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    id = 56 # int | 

    try:
        api_response = await api_instance.find_one_by_id(id)
        print("The response of IntegrationControllerApi->find_one_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->find_one_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**IntegrationDto**](IntegrationDto.md)

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

# **find_project_integration_by_id**
> ProjectIntegrationDto find_project_integration_by_id(integration_id, project_id)

### Example


```python
import src.client.generated
from src.client.generated.models.project_integration_dto import ProjectIntegrationDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    integration_id = 56 # int | 
    project_id = 56 # int | 

    try:
        api_response = await api_instance.find_project_integration_by_id(integration_id, project_id)
        print("The response of IntegrationControllerApi->find_project_integration_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->find_project_integration_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_id** | **int**|  | 
 **project_id** | **int**|  | 

### Return type

[**ProjectIntegrationDto**](ProjectIntegrationDto.md)

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

# **get_available_integrations**
> PageIntegrationInfoDto get_available_integrations(query=query, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_integration_info_dto import PageIntegrationInfoDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.get_available_integrations(query=query, page=page, size=size, sort=sort)
        print("The response of IntegrationControllerApi->get_available_integrations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->get_available_integrations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageIntegrationInfoDto**](PageIntegrationInfoDto.md)

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

# **get_global_fields**
> IntegrationFieldsFormDto get_global_fields(type, integration_id)

### Example


```python
import src.client.generated
from src.client.generated.models.integration_fields_form_dto import IntegrationFieldsFormDto
from src.client.generated.models.integration_type_dto import IntegrationTypeDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    type = src.client.generated.IntegrationTypeDto() # IntegrationTypeDto | 
    integration_id = 56 # int | 

    try:
        api_response = await api_instance.get_global_fields(type, integration_id)
        print("The response of IntegrationControllerApi->get_global_fields:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->get_global_fields: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | [**IntegrationTypeDto**](.md)|  | 
 **integration_id** | **int**|  | 

### Return type

[**IntegrationFieldsFormDto**](IntegrationFieldsFormDto.md)

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

# **get_integration_projects**
> PageProjectSuggestDto get_integration_projects(id, query=query, my=my, favorite=favorite, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_project_suggest_dto import PageProjectSuggestDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    id = 56 # int | 
    query = 'query_example' # str |  (optional)
    my = True # bool |  (optional)
    favorite = True # bool |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.get_integration_projects(id, query=query, my=my, favorite=favorite, page=page, size=size, sort=sort)
        print("The response of IntegrationControllerApi->get_integration_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->get_integration_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **query** | **str**|  | [optional] 
 **my** | **bool**|  | [optional] 
 **favorite** | **bool**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageProjectSuggestDto**](PageProjectSuggestDto.md)

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

# **get_integrations**
> PageIntegrationDto get_integrations(page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_integration_dto import PageIntegrationDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.get_integrations(page=page, size=size, sort=sort)
        print("The response of IntegrationControllerApi->get_integrations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->get_integrations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageIntegrationDto**](PageIntegrationDto.md)

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

# **get_project_available_integrations**
> PageIntegrationDto get_project_available_integrations(project_id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_integration_dto import PageIntegrationDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    project_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.get_project_available_integrations(project_id, page=page, size=size, sort=sort)
        print("The response of IntegrationControllerApi->get_project_available_integrations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->get_project_available_integrations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageIntegrationDto**](PageIntegrationDto.md)

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

# **get_project_integration_fields**
> ProjectIntegrationFieldsFormDto get_project_integration_fields(integration_id, project_id)

### Example


```python
import src.client.generated
from src.client.generated.models.project_integration_fields_form_dto import ProjectIntegrationFieldsFormDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    integration_id = 56 # int | 
    project_id = 56 # int | 

    try:
        api_response = await api_instance.get_project_integration_fields(integration_id, project_id)
        print("The response of IntegrationControllerApi->get_project_integration_fields:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->get_project_integration_fields: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_id** | **int**|  | 
 **project_id** | **int**|  | 

### Return type

[**ProjectIntegrationFieldsFormDto**](ProjectIntegrationFieldsFormDto.md)

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

# **get_project_integrations**
> PageProjectIntegrationDto get_project_integrations(project_id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_project_integration_dto import PageProjectIntegrationDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    project_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.get_project_integrations(project_id, page=page, size=size, sort=sort)
        print("The response of IntegrationControllerApi->get_project_integrations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->get_project_integrations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageProjectIntegrationDto**](PageProjectIntegrationDto.md)

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

# **patch34**
> IntegrationDto patch34(id, integration_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.integration_dto import IntegrationDto
from src.client.generated.models.integration_patch_dto import IntegrationPatchDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    id = 56 # int | 
    integration_patch_dto = src.client.generated.IntegrationPatchDto() # IntegrationPatchDto | 

    try:
        api_response = await api_instance.patch34(id, integration_patch_dto)
        print("The response of IntegrationControllerApi->patch34:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->patch34: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **integration_patch_dto** | [**IntegrationPatchDto**](IntegrationPatchDto.md)|  | 

### Return type

[**IntegrationDto**](IntegrationDto.md)

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

# **patch_project_integration**
> ProjectIntegrationDto patch_project_integration(integration_id, project_id, project_integration_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.project_integration_dto import ProjectIntegrationDto
from src.client.generated.models.project_integration_patch_dto import ProjectIntegrationPatchDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    integration_id = 56 # int | 
    project_id = 56 # int | 
    project_integration_patch_dto = src.client.generated.ProjectIntegrationPatchDto() # ProjectIntegrationPatchDto | 

    try:
        api_response = await api_instance.patch_project_integration(integration_id, project_id, project_integration_patch_dto)
        print("The response of IntegrationControllerApi->patch_project_integration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->patch_project_integration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_id** | **int**|  | 
 **project_id** | **int**|  | 
 **project_integration_patch_dto** | [**ProjectIntegrationPatchDto**](ProjectIntegrationPatchDto.md)|  | 

### Return type

[**ProjectIntegrationDto**](ProjectIntegrationDto.md)

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

# **suggest15**
> PageIdAndNameOnlyDto suggest15(query=query, project_id=project_id, id=id, ignore_id=ignore_id, operation=operation, integration_type=integration_type, page=page, size=size, sort=sort)

Suggest integrations

### Example


```python
import src.client.generated
from src.client.generated.models.integration_operation_type_dto import IntegrationOperationTypeDto
from src.client.generated.models.integration_type_dto import IntegrationTypeDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    project_id = 56 # int |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    operation = [src.client.generated.IntegrationOperationTypeDto()] # List[IntegrationOperationTypeDto] |  (optional)
    integration_type = [src.client.generated.IntegrationTypeDto()] # List[IntegrationTypeDto] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Suggest integrations
        api_response = await api_instance.suggest15(query=query, project_id=project_id, id=id, ignore_id=ignore_id, operation=operation, integration_type=integration_type, page=page, size=size, sort=sort)
        print("The response of IntegrationControllerApi->suggest15:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->suggest15: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | [optional] 
 **project_id** | **int**|  | [optional] 
 **id** | [**List[int]**](int.md)|  | [optional] 
 **ignore_id** | [**List[int]**](int.md)|  | [optional] 
 **operation** | [**List[IntegrationOperationTypeDto]**](IntegrationOperationTypeDto.md)|  | [optional] 
 **integration_type** | [**List[IntegrationTypeDto]**](IntegrationTypeDto.md)|  | [optional] 
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

# **validate1**
> validate1(integration_validate_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.integration_validate_dto import IntegrationValidateDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    integration_validate_dto = src.client.generated.IntegrationValidateDto() # IntegrationValidateDto | 

    try:
        await api_instance.validate1(integration_validate_dto)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->validate1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_validate_dto** | [**IntegrationValidateDto**](IntegrationValidateDto.md)|  | 

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

# **validate2**
> validate2(project_integration_validate_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.project_integration_validate_dto import ProjectIntegrationValidateDto
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
    api_instance = src.client.generated.IntegrationControllerApi(api_client)
    project_integration_validate_dto = src.client.generated.ProjectIntegrationValidateDto() # ProjectIntegrationValidateDto | 

    try:
        await api_instance.validate2(project_integration_validate_dto)
    except Exception as e:
        print("Exception when calling IntegrationControllerApi->validate2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_integration_validate_dto** | [**ProjectIntegrationValidateDto**](ProjectIntegrationValidateDto.md)|  | 

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

