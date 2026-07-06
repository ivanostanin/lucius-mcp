# src.client.generated.TestResultBulkControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**assign1**](TestResultBulkControllerApi.md#assign1) | **POST** /api/testresult/bulk/assign | Assign all selected test results
[**hide**](TestResultBulkControllerApi.md#hide) | **POST** /api/testresult/bulk/hide | Hide all selected test results
[**link_defects**](TestResultBulkControllerApi.md#link_defects) | **POST** /api/testresult/bulk/defect/link | Link defects for all selected test results
[**mute1**](TestResultBulkControllerApi.md#mute1) | **POST** /api/testresult/bulk/mute | Mute all selected test results
[**rerun**](TestResultBulkControllerApi.md#rerun) | **POST** /api/testresult/bulk/rerun | Rerun all selected test results
[**resolve2**](TestResultBulkControllerApi.md#resolve2) | **POST** /api/testresult/bulk/resolve | Resolve all selected test results
[**tags_add1**](TestResultBulkControllerApi.md#tags_add1) | **POST** /api/testresult/bulk/tag/add | Add tags for all selected test results
[**tags_remove1**](TestResultBulkControllerApi.md#tags_remove1) | **POST** /api/testresult/bulk/tag/remove | Remove tags for all selected test results
[**unmute1**](TestResultBulkControllerApi.md#unmute1) | **POST** /api/testresult/bulk/unmute | Unmute all selected test results


# **assign1**
> assign1(test_result_bulk_assign_dto)

Assign all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_assign_dto import TestResultBulkAssignDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_assign_dto = src.client.generated.TestResultBulkAssignDto() # TestResultBulkAssignDto | 

    try:
        # Assign all selected test results
        await api_instance.assign1(test_result_bulk_assign_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->assign1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_assign_dto** | [**TestResultBulkAssignDto**](TestResultBulkAssignDto.md)|  | 

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

# **hide**
> hide(test_result_bulk_dto)

Hide all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_dto import TestResultBulkDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_dto = src.client.generated.TestResultBulkDto() # TestResultBulkDto | 

    try:
        # Hide all selected test results
        await api_instance.hide(test_result_bulk_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->hide: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_dto** | [**TestResultBulkDto**](TestResultBulkDto.md)|  | 

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

# **link_defects**
> link_defects(test_result_bulk_entity_ids_dto)

Link defects for all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_entity_ids_dto import TestResultBulkEntityIdsDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_entity_ids_dto = src.client.generated.TestResultBulkEntityIdsDto() # TestResultBulkEntityIdsDto | 

    try:
        # Link defects for all selected test results
        await api_instance.link_defects(test_result_bulk_entity_ids_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->link_defects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_entity_ids_dto** | [**TestResultBulkEntityIdsDto**](TestResultBulkEntityIdsDto.md)|  | 

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

# **mute1**
> mute1(test_result_bulk_mute_dto)

Mute all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_mute_dto import TestResultBulkMuteDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_mute_dto = src.client.generated.TestResultBulkMuteDto() # TestResultBulkMuteDto | 

    try:
        # Mute all selected test results
        await api_instance.mute1(test_result_bulk_mute_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->mute1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_mute_dto** | [**TestResultBulkMuteDto**](TestResultBulkMuteDto.md)|  | 

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

# **rerun**
> rerun(test_result_bulk_rerun_dto)

Rerun all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_rerun_dto import TestResultBulkRerunDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_rerun_dto = src.client.generated.TestResultBulkRerunDto() # TestResultBulkRerunDto | 

    try:
        # Rerun all selected test results
        await api_instance.rerun(test_result_bulk_rerun_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->rerun: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_rerun_dto** | [**TestResultBulkRerunDto**](TestResultBulkRerunDto.md)|  | 

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

# **resolve2**
> resolve2(test_result_bulk_resolve_dto)

Resolve all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_resolve_dto import TestResultBulkResolveDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_resolve_dto = src.client.generated.TestResultBulkResolveDto() # TestResultBulkResolveDto | 

    try:
        # Resolve all selected test results
        await api_instance.resolve2(test_result_bulk_resolve_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->resolve2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_resolve_dto** | [**TestResultBulkResolveDto**](TestResultBulkResolveDto.md)|  | 

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

# **tags_add1**
> tags_add1(test_result_bulk_tag_dto)

Add tags for all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_tag_dto import TestResultBulkTagDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_tag_dto = src.client.generated.TestResultBulkTagDto() # TestResultBulkTagDto | 

    try:
        # Add tags for all selected test results
        await api_instance.tags_add1(test_result_bulk_tag_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->tags_add1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_tag_dto** | [**TestResultBulkTagDto**](TestResultBulkTagDto.md)|  | 

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

# **tags_remove1**
> tags_remove1(test_result_bulk_entity_ids_dto)

Remove tags for all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_entity_ids_dto import TestResultBulkEntityIdsDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_entity_ids_dto = src.client.generated.TestResultBulkEntityIdsDto() # TestResultBulkEntityIdsDto | 

    try:
        # Remove tags for all selected test results
        await api_instance.tags_remove1(test_result_bulk_entity_ids_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->tags_remove1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_entity_ids_dto** | [**TestResultBulkEntityIdsDto**](TestResultBulkEntityIdsDto.md)|  | 

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

# **unmute1**
> unmute1(test_result_bulk_dto)

Unmute all selected test results

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_bulk_dto import TestResultBulkDto
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
    api_instance = src.client.generated.TestResultBulkControllerApi(api_client)
    test_result_bulk_dto = src.client.generated.TestResultBulkDto() # TestResultBulkDto | 

    try:
        # Unmute all selected test results
        await api_instance.unmute1(test_result_bulk_dto)
    except Exception as e:
        print("Exception when calling TestResultBulkControllerApi->unmute1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_bulk_dto** | [**TestResultBulkDto**](TestResultBulkDto.md)|  | 

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

