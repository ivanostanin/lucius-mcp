# src.client.generated.ProjectControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**calculate_stats**](ProjectControllerApi.md#calculate_stats) | **GET** /api/project/{id}/stats | Find project stats by id
[**count_test_cases_in_projects**](ProjectControllerApi.md#count_test_cases_in_projects) | **GET** /api/project/count-test-cases | Count test cases in projects that use specified custom field
[**create25**](ProjectControllerApi.md#create25) | **POST** /api/project | Create a new project
[**delete23**](ProjectControllerApi.md#delete23) | **DELETE** /api/project/{id} | Delete project by id
[**find_all21**](ProjectControllerApi.md#find_all21) | **GET** /api/project | Find all projects
[**find_by_custom_field**](ProjectControllerApi.md#find_by_custom_field) | **GET** /api/project/customfield | Find projects that use/do not use specified custom field
[**find_one19**](ProjectControllerApi.md#find_one19) | **GET** /api/project/{id} | Find project by id
[**get_suggest**](ProjectControllerApi.md#get_suggest) | **GET** /api/project/suggest | Suggest projects
[**patch25**](ProjectControllerApi.md#patch25) | **PATCH** /api/project/{id} | Patch project
[**set_favorite**](ProjectControllerApi.md#set_favorite) | **POST** /api/project/{id}/favorite | Mark project as favorite


# **calculate_stats**
> ProjectStatsDto calculate_stats(id)

Find project stats by id

### Example


```python
import src.client.generated
from src.client.generated.models.project_stats_dto import ProjectStatsDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find project stats by id
        api_response = await api_instance.calculate_stats(id)
        print("The response of ProjectControllerApi->calculate_stats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->calculate_stats: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**ProjectStatsDto**](ProjectStatsDto.md)

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

# **count_test_cases_in_projects**
> List[ProjectTestCaseCountDto] count_test_cases_in_projects(id, custom_field_id, deleted=deleted)

Count test cases in projects that use specified custom field

### Example


```python
import src.client.generated
from src.client.generated.models.project_test_case_count_dto import ProjectTestCaseCountDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    id = [56] # List[int] | 
    custom_field_id = 56 # int | 
    deleted = True # bool |  (optional)

    try:
        # Count test cases in projects that use specified custom field
        api_response = await api_instance.count_test_cases_in_projects(id, custom_field_id, deleted=deleted)
        print("The response of ProjectControllerApi->count_test_cases_in_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->count_test_cases_in_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**List[int]**](int.md)|  | 
 **custom_field_id** | **int**|  | 
 **deleted** | **bool**|  | [optional] 

### Return type

[**List[ProjectTestCaseCountDto]**](ProjectTestCaseCountDto.md)

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

# **create25**
> ProjectDto create25(project_create_dto)

Create a new project

### Example


```python
import src.client.generated
from src.client.generated.models.project_create_dto import ProjectCreateDto
from src.client.generated.models.project_dto import ProjectDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    project_create_dto = src.client.generated.ProjectCreateDto() # ProjectCreateDto | 

    try:
        # Create a new project
        api_response = await api_instance.create25(project_create_dto)
        print("The response of ProjectControllerApi->create25:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->create25: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_create_dto** | [**ProjectCreateDto**](ProjectCreateDto.md)|  | 

### Return type

[**ProjectDto**](ProjectDto.md)

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

# **delete23**
> delete23(id)

Delete project by id

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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete project by id
        await api_instance.delete23(id)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->delete23: %s\n" % e)
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

# **find_all21**
> PageProjectDto find_all21(query=query, my=my, favorite=favorite, page=page, size=size, sort=sort)

Find all projects

### Example


```python
import src.client.generated
from src.client.generated.models.page_project_dto import PageProjectDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    my = True # bool |  (optional)
    favorite = True # bool |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find all projects
        api_response = await api_instance.find_all21(query=query, my=my, favorite=favorite, page=page, size=size, sort=sort)
        print("The response of ProjectControllerApi->find_all21:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->find_all21: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | [optional] 
 **my** | **bool**|  | [optional] 
 **favorite** | **bool**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageProjectDto**](PageProjectDto.md)

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

# **find_by_custom_field**
> PageProjectDto find_by_custom_field(custom_field_id, exclude=exclude, query=query, page=page, size=size, sort=sort)

Find projects that use/do not use specified custom field

### Example


```python
import src.client.generated
from src.client.generated.models.page_project_dto import PageProjectDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    custom_field_id = 56 # int | 
    exclude = True # bool |  (optional)
    query = 'query_example' # str |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find projects that use/do not use specified custom field
        api_response = await api_instance.find_by_custom_field(custom_field_id, exclude=exclude, query=query, page=page, size=size, sort=sort)
        print("The response of ProjectControllerApi->find_by_custom_field:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->find_by_custom_field: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_field_id** | **int**|  | 
 **exclude** | **bool**|  | [optional] 
 **query** | **str**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageProjectDto**](PageProjectDto.md)

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

# **find_one19**
> ProjectDto find_one19(id)

Find project by id

### Example


```python
import src.client.generated
from src.client.generated.models.project_dto import ProjectDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find project by id
        api_response = await api_instance.find_one19(id)
        print("The response of ProjectControllerApi->find_one19:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->find_one19: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**ProjectDto**](ProjectDto.md)

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

# **get_suggest**
> PageProjectSuggestDto get_suggest(query=query, id=id, ignore_id=ignore_id, write=write, page=page, size=size, sort=sort)

Suggest projects

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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    write = False # bool |  (optional) (default to False)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Suggest projects
        api_response = await api_instance.get_suggest(query=query, id=id, ignore_id=ignore_id, write=write, page=page, size=size, sort=sort)
        print("The response of ProjectControllerApi->get_suggest:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->get_suggest: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | [optional] 
 **id** | [**List[int]**](int.md)|  | [optional] 
 **ignore_id** | [**List[int]**](int.md)|  | [optional] 
 **write** | **bool**|  | [optional] [default to False]
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

# **patch25**
> ProjectDto patch25(id, project_patch_dto)

Patch project

### Example


```python
import src.client.generated
from src.client.generated.models.project_dto import ProjectDto
from src.client.generated.models.project_patch_dto import ProjectPatchDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    id = 56 # int | 
    project_patch_dto = src.client.generated.ProjectPatchDto() # ProjectPatchDto | 

    try:
        # Patch project
        api_response = await api_instance.patch25(id, project_patch_dto)
        print("The response of ProjectControllerApi->patch25:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->patch25: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **project_patch_dto** | [**ProjectPatchDto**](ProjectPatchDto.md)|  | 

### Return type

[**ProjectDto**](ProjectDto.md)

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

# **set_favorite**
> ProjectDto set_favorite(id, favorite=favorite)

Mark project as favorite

### Example


```python
import src.client.generated
from src.client.generated.models.project_dto import ProjectDto
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
    api_instance = src.client.generated.ProjectControllerApi(api_client)
    id = 56 # int | 
    favorite = True # bool |  (optional)

    try:
        # Mark project as favorite
        api_response = await api_instance.set_favorite(id, favorite=favorite)
        print("The response of ProjectControllerApi->set_favorite:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectControllerApi->set_favorite: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **favorite** | **bool**|  | [optional] 

### Return type

[**ProjectDto**](ProjectDto.md)

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

