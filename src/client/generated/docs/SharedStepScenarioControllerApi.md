# src.client.generated.SharedStepScenarioControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**copy**](SharedStepScenarioControllerApi.md#copy) | **POST** /api/sharedstep/step/{id}/copy | Copy scenario step
[**create20**](SharedStepScenarioControllerApi.md#create20) | **POST** /api/sharedstep/step | Create scenario step
[**delete_by_id2**](SharedStepScenarioControllerApi.md#delete_by_id2) | **DELETE** /api/sharedstep/step/{id} | Delete a specified scenario step
[**delete_scenario1**](SharedStepScenarioControllerApi.md#delete_scenario1) | **DELETE** /api/sharedstep/{id}/scenario | Delete scenario for test case
[**find_one40**](SharedStepScenarioControllerApi.md#find_one40) | **GET** /api/sharedstep/{id}/step | Get scenario for shared step
[**move2**](SharedStepScenarioControllerApi.md#move2) | **POST** /api/sharedstep/step/{id}/move | Move scenario step
[**patch_by_id1**](SharedStepScenarioControllerApi.md#patch_by_id1) | **PATCH** /api/sharedstep/step/{id} | Patch a specified scenario step
[**set_shared_step_scenario**](SharedStepScenarioControllerApi.md#set_shared_step_scenario) | **POST** /api/sharedstep/{id}/scenario | Set new scenario for ss
[**usage**](SharedStepScenarioControllerApi.md#usage) | **GET** /api/sharedstep/{id}/usage | Get testcases with usage of shared step


# **copy**
> NormalizedScenarioDto copy(id, scenario_step_copy_dto)

Copy scenario step

### Example


```python
import src.client.generated
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
from src.client.generated.models.scenario_step_copy_dto import ScenarioStepCopyDto
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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 
    scenario_step_copy_dto = src.client.generated.ScenarioStepCopyDto() # ScenarioStepCopyDto | 

    try:
        # Copy scenario step
        api_response = await api_instance.copy(id, scenario_step_copy_dto)
        print("The response of SharedStepScenarioControllerApi->copy:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->copy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **scenario_step_copy_dto** | [**ScenarioStepCopyDto**](ScenarioStepCopyDto.md)|  | 

### Return type

[**NormalizedScenarioDto**](NormalizedScenarioDto.md)

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

# **create20**
> ScenarioStepCreatedResponseDto create20(scenario_step_create_dto, before_id=before_id, after_id=after_id, with_expected_result=with_expected_result)

Create scenario step

### Example


```python
import src.client.generated
from src.client.generated.models.scenario_step_create_dto import ScenarioStepCreateDto
from src.client.generated.models.scenario_step_created_response_dto import ScenarioStepCreatedResponseDto
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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    scenario_step_create_dto = src.client.generated.ScenarioStepCreateDto() # ScenarioStepCreateDto | 
    before_id = 56 # int |  (optional)
    after_id = 56 # int |  (optional)
    with_expected_result = False # bool |  (optional) (default to False)

    try:
        # Create scenario step
        api_response = await api_instance.create20(scenario_step_create_dto, before_id=before_id, after_id=after_id, with_expected_result=with_expected_result)
        print("The response of SharedStepScenarioControllerApi->create20:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->create20: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scenario_step_create_dto** | [**ScenarioStepCreateDto**](ScenarioStepCreateDto.md)|  | 
 **before_id** | **int**|  | [optional] 
 **after_id** | **int**|  | [optional] 
 **with_expected_result** | **bool**|  | [optional] [default to False]

### Return type

[**ScenarioStepCreatedResponseDto**](ScenarioStepCreatedResponseDto.md)

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

# **delete_by_id2**
> NormalizedScenarioDto delete_by_id2(id)

Delete a specified scenario step

### Example


```python
import src.client.generated
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete a specified scenario step
        api_response = await api_instance.delete_by_id2(id)
        print("The response of SharedStepScenarioControllerApi->delete_by_id2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->delete_by_id2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**NormalizedScenarioDto**](NormalizedScenarioDto.md)

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

# **delete_scenario1**
> delete_scenario1(id)

Delete scenario for test case

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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete scenario for test case
        await api_instance.delete_scenario1(id)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->delete_scenario1: %s\n" % e)
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
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **find_one40**
> NormalizedScenarioDto find_one40(id)

Get scenario for shared step

### Example


```python
import src.client.generated
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Get scenario for shared step
        api_response = await api_instance.find_one40(id)
        print("The response of SharedStepScenarioControllerApi->find_one40:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->find_one40: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**NormalizedScenarioDto**](NormalizedScenarioDto.md)

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

# **move2**
> NormalizedScenarioDto move2(id, scenario_step_move_dto)

Move scenario step

### Example


```python
import src.client.generated
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
from src.client.generated.models.scenario_step_move_dto import ScenarioStepMoveDto
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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 
    scenario_step_move_dto = src.client.generated.ScenarioStepMoveDto() # ScenarioStepMoveDto | 

    try:
        # Move scenario step
        api_response = await api_instance.move2(id, scenario_step_move_dto)
        print("The response of SharedStepScenarioControllerApi->move2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->move2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **scenario_step_move_dto** | [**ScenarioStepMoveDto**](ScenarioStepMoveDto.md)|  | 

### Return type

[**NormalizedScenarioDto**](NormalizedScenarioDto.md)

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

# **patch_by_id1**
> NormalizedScenarioDto patch_by_id1(id, scenario_step_patch_dto, with_expected_result=with_expected_result)

Patch a specified scenario step

### Example


```python
import src.client.generated
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
from src.client.generated.models.scenario_step_patch_dto import ScenarioStepPatchDto
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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 
    scenario_step_patch_dto = src.client.generated.ScenarioStepPatchDto() # ScenarioStepPatchDto | 
    with_expected_result = False # bool |  (optional) (default to False)

    try:
        # Patch a specified scenario step
        api_response = await api_instance.patch_by_id1(id, scenario_step_patch_dto, with_expected_result=with_expected_result)
        print("The response of SharedStepScenarioControllerApi->patch_by_id1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->patch_by_id1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **scenario_step_patch_dto** | [**ScenarioStepPatchDto**](ScenarioStepPatchDto.md)|  | 
 **with_expected_result** | **bool**|  | [optional] [default to False]

### Return type

[**NormalizedScenarioDto**](NormalizedScenarioDto.md)

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

# **set_shared_step_scenario**
> NormalizedScenarioDto set_shared_step_scenario(id, shared_step_scenario_dto)

Set new scenario for ss

### Example


```python
import src.client.generated
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
from src.client.generated.models.shared_step_scenario_dto import SharedStepScenarioDto
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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 
    shared_step_scenario_dto = src.client.generated.SharedStepScenarioDto() # SharedStepScenarioDto | 

    try:
        # Set new scenario for ss
        api_response = await api_instance.set_shared_step_scenario(id, shared_step_scenario_dto)
        print("The response of SharedStepScenarioControllerApi->set_shared_step_scenario:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->set_shared_step_scenario: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **shared_step_scenario_dto** | [**SharedStepScenarioDto**](SharedStepScenarioDto.md)|  | 

### Return type

[**NormalizedScenarioDto**](NormalizedScenarioDto.md)

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

# **usage**
> PageTestCaseRowDto usage(id, page=page, size=size, sort=sort)

Get testcases with usage of shared step

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
    api_instance = src.client.generated.SharedStepScenarioControllerApi(api_client)
    id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [createdDate,DESC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [createdDate,DESC])

    try:
        # Get testcases with usage of shared step
        api_response = await api_instance.usage(id, page=page, size=size, sort=sort)
        print("The response of SharedStepScenarioControllerApi->usage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepScenarioControllerApi->usage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [createdDate,DESC]]

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

