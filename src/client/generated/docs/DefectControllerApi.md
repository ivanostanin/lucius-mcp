# src.client.generated.DefectControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create45**](DefectControllerApi.md#create45) | **POST** /api/defect | 
[**create_issue**](DefectControllerApi.md#create_issue) | **POST** /api/defect/{id}/createissue | 
[**delete37**](DefectControllerApi.md#delete37) | **DELETE** /api/defect/{id} | 
[**find_all_by_project_id**](DefectControllerApi.md#find_all_by_project_id) | **GET** /api/defect | 
[**find_by_id1**](DefectControllerApi.md#find_by_id1) | **GET** /api/defect/{id} | 
[**get_launches**](DefectControllerApi.md#get_launches) | **GET** /api/defect/{id}/launch | 
[**get_matchers**](DefectControllerApi.md#get_matchers) | **GET** /api/defect/{id}/matcher | 
[**get_test_cases2**](DefectControllerApi.md#get_test_cases2) | **GET** /api/defect/{id}/testcase | 
[**get_test_results**](DefectControllerApi.md#get_test_results) | **GET** /api/defect/{id}/testresult | 
[**link_issue**](DefectControllerApi.md#link_issue) | **POST** /api/defect/{id}/issue | 
[**patch42**](DefectControllerApi.md#patch42) | **PATCH** /api/defect/{id} | 
[**suggest20**](DefectControllerApi.md#suggest20) | **GET** /api/defect/suggest | 
[**unlink_issue**](DefectControllerApi.md#unlink_issue) | **DELETE** /api/defect/{id}/issue | 


# **create45**
> DefectOverviewDto create45(defect_create_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_create_dto import DefectCreateDto
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    defect_create_dto = src.client.generated.DefectCreateDto() # DefectCreateDto | 

    try:
        api_response = await api_instance.create45(defect_create_dto)
        print("The response of DefectControllerApi->create45:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->create45: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **defect_create_dto** | [**DefectCreateDto**](DefectCreateDto.md)|  | 

### Return type

[**DefectOverviewDto**](DefectOverviewDto.md)

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

# **create_issue**
> DefectOverviewDto create_issue(id, issue_to_create_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
from src.client.generated.models.issue_to_create_dto import IssueToCreateDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 
    issue_to_create_dto = src.client.generated.IssueToCreateDto() # IssueToCreateDto | 

    try:
        api_response = await api_instance.create_issue(id, issue_to_create_dto)
        print("The response of DefectControllerApi->create_issue:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->create_issue: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **issue_to_create_dto** | [**IssueToCreateDto**](IssueToCreateDto.md)|  | 

### Return type

[**DefectOverviewDto**](DefectOverviewDto.md)

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

# **delete37**
> delete37(id)

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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 

    try:
        await api_instance.delete37(id)
    except Exception as e:
        print("Exception when calling DefectControllerApi->delete37: %s\n" % e)
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

# **find_all_by_project_id**
> PageDefectCountRowDto find_all_by_project_id(project_id, name_filter=name_filter, status=status, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_defect_count_row_dto import PageDefectCountRowDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    project_id = 56 # int | 
    name_filter = 'name_filter_example' # str |  (optional)
    status = ['status_example'] # List[str] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 20 # int | The size of the page to be returned (optional) (default to 20)
    sort = ['sort_example'] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional)

    try:
        api_response = await api_instance.find_all_by_project_id(project_id, name_filter=name_filter, status=status, page=page, size=size, sort=sort)
        print("The response of DefectControllerApi->find_all_by_project_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->find_all_by_project_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **name_filter** | **str**|  | [optional] 
 **status** | [**List[str]**](str.md)|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 20]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] 

### Return type

[**PageDefectCountRowDto**](PageDefectCountRowDto.md)

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

# **find_by_id1**
> DefectOverviewDto find_by_id1(id)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 

    try:
        api_response = await api_instance.find_by_id1(id)
        print("The response of DefectControllerApi->find_by_id1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->find_by_id1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**DefectOverviewDto**](DefectOverviewDto.md)

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

# **get_launches**
> PageLaunchRowDto get_launches(id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_launch_row_dto import PageLaunchRowDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = ["created_date,DESC"] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to ["created_date,DESC"])

    try:
        api_response = await api_instance.get_launches(id, page=page, size=size, sort=sort)
        print("The response of DefectControllerApi->get_launches:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->get_launches: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [&quot;created_date,DESC&quot;]]

### Return type

[**PageLaunchRowDto**](PageLaunchRowDto.md)

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

# **get_matchers**
> PageDefectMatcherDto get_matchers(id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_defect_matcher_dto import PageDefectMatcherDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [id,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [id,ASC])

    try:
        api_response = await api_instance.get_matchers(id, page=page, size=size, sort=sort)
        print("The response of DefectControllerApi->get_matchers:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->get_matchers: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [id,ASC]]

### Return type

[**PageDefectMatcherDto**](PageDefectMatcherDto.md)

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

# **get_test_cases2**
> PageTestCaseRowDto get_test_cases2(id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_row_dto import PageTestCaseRowDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [id,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [id,ASC])

    try:
        api_response = await api_instance.get_test_cases2(id, page=page, size=size, sort=sort)
        print("The response of DefectControllerApi->get_test_cases2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->get_test_cases2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [id,ASC]]

### Return type

[**PageTestCaseRowDto**](PageTestCaseRowDto.md)

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

# **get_test_results**
> PageTestResultRowDto get_test_results(id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_result_row_dto import PageTestResultRowDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [created_date,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [created_date,DESC])

    try:
        api_response = await api_instance.get_test_results(id, page=page, size=size, sort=sort)
        print("The response of DefectControllerApi->get_test_results:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->get_test_results: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [created_date,DESC]]

### Return type

[**PageTestResultRowDto**](PageTestResultRowDto.md)

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

# **link_issue**
> DefectOverviewDto link_issue(id, defect_issue_link_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_issue_link_dto import DefectIssueLinkDto
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 
    defect_issue_link_dto = src.client.generated.DefectIssueLinkDto() # DefectIssueLinkDto | 

    try:
        api_response = await api_instance.link_issue(id, defect_issue_link_dto)
        print("The response of DefectControllerApi->link_issue:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->link_issue: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **defect_issue_link_dto** | [**DefectIssueLinkDto**](DefectIssueLinkDto.md)|  | 

### Return type

[**DefectOverviewDto**](DefectOverviewDto.md)

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

# **patch42**
> DefectOverviewDto patch42(id, defect_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
from src.client.generated.models.defect_patch_dto import DefectPatchDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 
    defect_patch_dto = src.client.generated.DefectPatchDto() # DefectPatchDto | 

    try:
        api_response = await api_instance.patch42(id, defect_patch_dto)
        print("The response of DefectControllerApi->patch42:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->patch42: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **defect_patch_dto** | [**DefectPatchDto**](DefectPatchDto.md)|  | 

### Return type

[**DefectOverviewDto**](DefectOverviewDto.md)

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

# **suggest20**
> PageIdAndNameOnlyDto suggest20(query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    query = 'query_example' # str |  (optional)
    project_id = 56 # int |  (optional)
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.suggest20(query=query, project_id=project_id, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of DefectControllerApi->suggest20:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->suggest20: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **unlink_issue**
> DefectOverviewDto unlink_issue(id)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
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
    api_instance = src.client.generated.DefectControllerApi(api_client)
    id = 56 # int | 

    try:
        api_response = await api_instance.unlink_issue(id)
        print("The response of DefectControllerApi->unlink_issue:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectControllerApi->unlink_issue: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**DefectOverviewDto**](DefectOverviewDto.md)

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

