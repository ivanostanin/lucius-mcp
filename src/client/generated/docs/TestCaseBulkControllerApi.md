# src.client.generated.TestCaseBulkControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cfv_add1**](TestCaseBulkControllerApi.md#cfv_add1) | **POST** /api/testcase/bulk/cfv/add | Add custom field values for all test cases
[**cfv_remove1**](TestCaseBulkControllerApi.md#cfv_remove1) | **POST** /api/testcase/bulk/cfv/remove | Remove custom field values for all test cases
[**clone_all1**](TestCaseBulkControllerApi.md#clone_all1) | **POST** /api/testcase/bulk/clone | Clone test cases by ids
[**create_test_plan1**](TestCaseBulkControllerApi.md#create_test_plan1) | **POST** /api/testcase/bulk/testplan/create | Create test plan from selected test cases
[**delete_all1**](TestCaseBulkControllerApi.md#delete_all1) | **POST** /api/testcase/bulk/remove | Remove test cases by ids
[**drag_and_drop1**](TestCaseBulkControllerApi.md#drag_and_drop1) | **POST** /api/testcase/bulk/draganddrop | dragAndDrop test cases for trees
[**external_link_add1**](TestCaseBulkControllerApi.md#external_link_add1) | **POST** /api/testcase/bulk/externallink/add | Add external link for all test cases
[**issue_add1**](TestCaseBulkControllerApi.md#issue_add1) | **POST** /api/testcase/bulk/issue/add | Add issues for all test cases
[**issue_remove1**](TestCaseBulkControllerApi.md#issue_remove1) | **POST** /api/testcase/bulk/issue/remove | Remove issues for all test cases
[**layer_set1**](TestCaseBulkControllerApi.md#layer_set1) | **POST** /api/testcase/bulk/layer/set | Set specified layer for all test cases
[**member_add1**](TestCaseBulkControllerApi.md#member_add1) | **POST** /api/testcase/bulk/member/add | Add members for all test cases
[**member_remove1**](TestCaseBulkControllerApi.md#member_remove1) | **POST** /api/testcase/bulk/member/remove | Remove member for all test cases
[**move_all1**](TestCaseBulkControllerApi.md#move_all1) | **POST** /api/testcase/bulk/move | Move test cases to other project
[**mute_add1**](TestCaseBulkControllerApi.md#mute_add1) | **POST** /api/testcase/bulk/mute/add | Add mute for all test cases
[**run4**](TestCaseBulkControllerApi.md#run4) | **POST** /api/testcase/bulk/run | Run selected test cases in a new launch
[**run5**](TestCaseBulkControllerApi.md#run5) | **POST** /api/testcase/bulk/run/new | Run selected test cases in a new launch
[**run6**](TestCaseBulkControllerApi.md#run6) | **POST** /api/testcase/bulk/run/existing | Run selected test cases in an existing launch
[**status_set1**](TestCaseBulkControllerApi.md#status_set1) | **POST** /api/testcase/bulk/status/set | Set specified status for all test cases
[**tags_add2**](TestCaseBulkControllerApi.md#tags_add2) | **POST** /api/testcase/bulk/tag/add | Add tags for all test cases
[**tags_remove2**](TestCaseBulkControllerApi.md#tags_remove2) | **POST** /api/testcase/bulk/tag/remove | Remove tags for all test cases


# **cfv_add1**
> cfv_add1(test_case_bulk_new_cfv_dto)

Add custom field values for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_new_cfv_dto import TestCaseBulkNewCfvDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_new_cfv_dto = src.client.generated.TestCaseBulkNewCfvDto() # TestCaseBulkNewCfvDto | 

    try:
        # Add custom field values for all test cases
        await api_instance.cfv_add1(test_case_bulk_new_cfv_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->cfv_add1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_new_cfv_dto** | [**TestCaseBulkNewCfvDto**](TestCaseBulkNewCfvDto.md)|  | 

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

# **cfv_remove1**
> cfv_remove1(test_case_bulk_entity_ids_dto)

Remove custom field values for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_entity_ids_dto import TestCaseBulkEntityIdsDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_entity_ids_dto = src.client.generated.TestCaseBulkEntityIdsDto() # TestCaseBulkEntityIdsDto | 

    try:
        # Remove custom field values for all test cases
        await api_instance.cfv_remove1(test_case_bulk_entity_ids_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->cfv_remove1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_entity_ids_dto** | [**TestCaseBulkEntityIdsDto**](TestCaseBulkEntityIdsDto.md)|  | 

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

# **clone_all1**
> clone_all1(test_case_bulk_clone_dto)

Clone test cases by ids

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_clone_dto import TestCaseBulkCloneDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_clone_dto = src.client.generated.TestCaseBulkCloneDto() # TestCaseBulkCloneDto | 

    try:
        # Clone test cases by ids
        await api_instance.clone_all1(test_case_bulk_clone_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->clone_all1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_clone_dto** | [**TestCaseBulkCloneDto**](TestCaseBulkCloneDto.md)|  | 

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

# **create_test_plan1**
> TestPlanDto create_test_plan1(test_case_bulk_test_plan_create_dto)

Create test plan from selected test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_test_plan_create_dto import TestCaseBulkTestPlanCreateDto
from src.client.generated.models.test_plan_dto import TestPlanDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_test_plan_create_dto = src.client.generated.TestCaseBulkTestPlanCreateDto() # TestCaseBulkTestPlanCreateDto | 

    try:
        # Create test plan from selected test cases
        api_response = await api_instance.create_test_plan1(test_case_bulk_test_plan_create_dto)
        print("The response of TestCaseBulkControllerApi->create_test_plan1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->create_test_plan1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_test_plan_create_dto** | [**TestCaseBulkTestPlanCreateDto**](TestCaseBulkTestPlanCreateDto.md)|  | 

### Return type

[**TestPlanDto**](TestPlanDto.md)

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

# **delete_all1**
> delete_all1(test_case_bulk_dto)

Remove test cases by ids

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_dto import TestCaseBulkDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_dto = src.client.generated.TestCaseBulkDto() # TestCaseBulkDto | 

    try:
        # Remove test cases by ids
        await api_instance.delete_all1(test_case_bulk_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->delete_all1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_dto** | [**TestCaseBulkDto**](TestCaseBulkDto.md)|  | 

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

# **drag_and_drop1**
> drag_and_drop1(test_case_bulk_drag_and_drop_dto)

dragAndDrop test cases for trees

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_drag_and_drop_dto import TestCaseBulkDragAndDropDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_drag_and_drop_dto = src.client.generated.TestCaseBulkDragAndDropDto() # TestCaseBulkDragAndDropDto | 

    try:
        # dragAndDrop test cases for trees
        await api_instance.drag_and_drop1(test_case_bulk_drag_and_drop_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->drag_and_drop1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_drag_and_drop_dto** | [**TestCaseBulkDragAndDropDto**](TestCaseBulkDragAndDropDto.md)|  | 

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

# **external_link_add1**
> external_link_add1(test_case_bulk_external_link_dto)

Add external link for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_external_link_dto import TestCaseBulkExternalLinkDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_external_link_dto = src.client.generated.TestCaseBulkExternalLinkDto() # TestCaseBulkExternalLinkDto | 

    try:
        # Add external link for all test cases
        await api_instance.external_link_add1(test_case_bulk_external_link_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->external_link_add1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_external_link_dto** | [**TestCaseBulkExternalLinkDto**](TestCaseBulkExternalLinkDto.md)|  | 

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

# **issue_add1**
> issue_add1(test_case_bulk_issue_dto)

Add issues for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_issue_dto import TestCaseBulkIssueDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_issue_dto = src.client.generated.TestCaseBulkIssueDto() # TestCaseBulkIssueDto | 

    try:
        # Add issues for all test cases
        await api_instance.issue_add1(test_case_bulk_issue_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->issue_add1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_issue_dto** | [**TestCaseBulkIssueDto**](TestCaseBulkIssueDto.md)|  | 

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

# **issue_remove1**
> issue_remove1(test_case_bulk_entity_ids_dto)

Remove issues for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_entity_ids_dto import TestCaseBulkEntityIdsDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_entity_ids_dto = src.client.generated.TestCaseBulkEntityIdsDto() # TestCaseBulkEntityIdsDto | 

    try:
        # Remove issues for all test cases
        await api_instance.issue_remove1(test_case_bulk_entity_ids_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->issue_remove1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_entity_ids_dto** | [**TestCaseBulkEntityIdsDto**](TestCaseBulkEntityIdsDto.md)|  | 

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

# **layer_set1**
> layer_set1(test_case_bulk_layer_dto)

Set specified layer for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_layer_dto import TestCaseBulkLayerDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_layer_dto = src.client.generated.TestCaseBulkLayerDto() # TestCaseBulkLayerDto | 

    try:
        # Set specified layer for all test cases
        await api_instance.layer_set1(test_case_bulk_layer_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->layer_set1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_layer_dto** | [**TestCaseBulkLayerDto**](TestCaseBulkLayerDto.md)|  | 

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

# **member_add1**
> member_add1(test_case_bulk_member_dto)

Add members for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_member_dto import TestCaseBulkMemberDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_member_dto = src.client.generated.TestCaseBulkMemberDto() # TestCaseBulkMemberDto | 

    try:
        # Add members for all test cases
        await api_instance.member_add1(test_case_bulk_member_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->member_add1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_member_dto** | [**TestCaseBulkMemberDto**](TestCaseBulkMemberDto.md)|  | 

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

# **member_remove1**
> member_remove1(test_case_bulk_entity_ids_dto)

Remove member for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_entity_ids_dto import TestCaseBulkEntityIdsDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_entity_ids_dto = src.client.generated.TestCaseBulkEntityIdsDto() # TestCaseBulkEntityIdsDto | 

    try:
        # Remove member for all test cases
        await api_instance.member_remove1(test_case_bulk_entity_ids_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->member_remove1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_entity_ids_dto** | [**TestCaseBulkEntityIdsDto**](TestCaseBulkEntityIdsDto.md)|  | 

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

# **move_all1**
> move_all1(test_case_bulk_project_change_dto)

Move test cases to other project

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_project_change_dto import TestCaseBulkProjectChangeDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_project_change_dto = src.client.generated.TestCaseBulkProjectChangeDto() # TestCaseBulkProjectChangeDto | 

    try:
        # Move test cases to other project
        await api_instance.move_all1(test_case_bulk_project_change_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->move_all1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_project_change_dto** | [**TestCaseBulkProjectChangeDto**](TestCaseBulkProjectChangeDto.md)|  | 

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

# **mute_add1**
> mute_add1(test_case_bulk_mute_dto)

Add mute for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_mute_dto import TestCaseBulkMuteDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_mute_dto = src.client.generated.TestCaseBulkMuteDto() # TestCaseBulkMuteDto | 

    try:
        # Add mute for all test cases
        await api_instance.mute_add1(test_case_bulk_mute_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->mute_add1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_mute_dto** | [**TestCaseBulkMuteDto**](TestCaseBulkMuteDto.md)|  | 

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

# **run4**
> LaunchDto run4(test_case_bulk_run_new_launch_dto)

Run selected test cases in a new launch

### Example


```python
import src.client.generated
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.test_case_bulk_run_new_launch_dto import TestCaseBulkRunNewLaunchDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_run_new_launch_dto = src.client.generated.TestCaseBulkRunNewLaunchDto() # TestCaseBulkRunNewLaunchDto | 

    try:
        # Run selected test cases in a new launch
        api_response = await api_instance.run4(test_case_bulk_run_new_launch_dto)
        print("The response of TestCaseBulkControllerApi->run4:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->run4: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_run_new_launch_dto** | [**TestCaseBulkRunNewLaunchDto**](TestCaseBulkRunNewLaunchDto.md)|  | 

### Return type

[**LaunchDto**](LaunchDto.md)

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

# **run5**
> LaunchDto run5(test_case_bulk_run_new_launch_dto)

Run selected test cases in a new launch

### Example


```python
import src.client.generated
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.test_case_bulk_run_new_launch_dto import TestCaseBulkRunNewLaunchDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_run_new_launch_dto = src.client.generated.TestCaseBulkRunNewLaunchDto() # TestCaseBulkRunNewLaunchDto | 

    try:
        # Run selected test cases in a new launch
        api_response = await api_instance.run5(test_case_bulk_run_new_launch_dto)
        print("The response of TestCaseBulkControllerApi->run5:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->run5: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_run_new_launch_dto** | [**TestCaseBulkRunNewLaunchDto**](TestCaseBulkRunNewLaunchDto.md)|  | 

### Return type

[**LaunchDto**](LaunchDto.md)

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

# **run6**
> LaunchDto run6(test_case_bulk_run_existing_launch_dto)

Run selected test cases in an existing launch

### Example


```python
import src.client.generated
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.test_case_bulk_run_existing_launch_dto import TestCaseBulkRunExistingLaunchDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_run_existing_launch_dto = src.client.generated.TestCaseBulkRunExistingLaunchDto() # TestCaseBulkRunExistingLaunchDto | 

    try:
        # Run selected test cases in an existing launch
        api_response = await api_instance.run6(test_case_bulk_run_existing_launch_dto)
        print("The response of TestCaseBulkControllerApi->run6:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->run6: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_run_existing_launch_dto** | [**TestCaseBulkRunExistingLaunchDto**](TestCaseBulkRunExistingLaunchDto.md)|  | 

### Return type

[**LaunchDto**](LaunchDto.md)

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

# **status_set1**
> status_set1(test_case_bulk_status_dto)

Set specified status for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_status_dto import TestCaseBulkStatusDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_status_dto = src.client.generated.TestCaseBulkStatusDto() # TestCaseBulkStatusDto | 

    try:
        # Set specified status for all test cases
        await api_instance.status_set1(test_case_bulk_status_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->status_set1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_status_dto** | [**TestCaseBulkStatusDto**](TestCaseBulkStatusDto.md)|  | 

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

# **tags_add2**
> tags_add2(test_case_bulk_tag_dto)

Add tags for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_tag_dto import TestCaseBulkTagDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_tag_dto = src.client.generated.TestCaseBulkTagDto() # TestCaseBulkTagDto | 

    try:
        # Add tags for all test cases
        await api_instance.tags_add2(test_case_bulk_tag_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->tags_add2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_tag_dto** | [**TestCaseBulkTagDto**](TestCaseBulkTagDto.md)|  | 

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

# **tags_remove2**
> tags_remove2(test_case_bulk_entity_ids_dto)

Remove tags for all test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_bulk_entity_ids_dto import TestCaseBulkEntityIdsDto
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
    api_instance = src.client.generated.TestCaseBulkControllerApi(api_client)
    test_case_bulk_entity_ids_dto = src.client.generated.TestCaseBulkEntityIdsDto() # TestCaseBulkEntityIdsDto | 

    try:
        # Remove tags for all test cases
        await api_instance.tags_remove2(test_case_bulk_entity_ids_dto)
    except Exception as e:
        print("Exception when calling TestCaseBulkControllerApi->tags_remove2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_bulk_entity_ids_dto** | [**TestCaseBulkEntityIdsDto**](TestCaseBulkEntityIdsDto.md)|  | 

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

