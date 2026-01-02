# src.client.generated.TestCaseScenarioControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create15**](TestCaseScenarioControllerApi.md#create15) | **POST** /api/testcase/step | Create scenario step
[**delete_by_id1**](TestCaseScenarioControllerApi.md#delete_by_id1) | **DELETE** /api/testcase/step/{id} | Delete a specified scenario step
[**delete_scenario**](TestCaseScenarioControllerApi.md#delete_scenario) | **DELETE** /api/testcase/{id}/scenario | Delete scenario for test case
[**get_normalized_scenario**](TestCaseScenarioControllerApi.md#get_normalized_scenario) | **GET** /api/testcase/{id}/step | Get scenario for test case
[**get_scenario**](TestCaseScenarioControllerApi.md#get_scenario) | **GET** /api/testcase/{id}/scenario | Find scenario for test case
[**get_scenario_from_last_run**](TestCaseScenarioControllerApi.md#get_scenario_from_last_run) | **GET** /api/testcase/{id}/scenariofromrun | Find scenario for test case from last run
[**migrate_scenario**](TestCaseScenarioControllerApi.md#migrate_scenario) | **POST** /api/testcase/{id}/migrate | Migrate scenario for test case
[**move**](TestCaseScenarioControllerApi.md#move) | **POST** /api/testcase/step/{id}/move | Move scenario step
[**move1**](TestCaseScenarioControllerApi.md#move1) | **POST** /api/testcase/step/{id}/copy | Copy scenario step
[**patch_by_id**](TestCaseScenarioControllerApi.md#patch_by_id) | **PATCH** /api/testcase/step/{id} | Patch a specified scenario step
[**set_test_case_scenario**](TestCaseScenarioControllerApi.md#set_test_case_scenario) | **POST** /api/testcase/{id}/scenario | Set new type scenario for test case


# **create15**
> ScenarioStepCreatedResponseDto create15(scenario_step_create_dto, before_id=before_id, after_id=after_id, with_expected_result=with_expected_result)

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    scenario_step_create_dto = src.client.generated.ScenarioStepCreateDto() # ScenarioStepCreateDto | 
    before_id = 56 # int |  (optional)
    after_id = 56 # int |  (optional)
    with_expected_result = False # bool |  (optional) (default to False)

    try:
        # Create scenario step
        api_response = await api_instance.create15(scenario_step_create_dto, before_id=before_id, after_id=after_id, with_expected_result=with_expected_result)
        print("The response of TestCaseScenarioControllerApi->create15:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->create15: %s\n" % e)
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

# **delete_by_id1**
> NormalizedScenarioDto delete_by_id1(id)

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete a specified scenario step
        api_response = await api_instance.delete_by_id1(id)
        print("The response of TestCaseScenarioControllerApi->delete_by_id1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->delete_by_id1: %s\n" % e)
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

# **delete_scenario**
> delete_scenario(id)

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete scenario for test case
        await api_instance.delete_scenario(id)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->delete_scenario: %s\n" % e)
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

# **get_normalized_scenario**
> NormalizedScenarioDto get_normalized_scenario(id)

Get scenario for test case

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Get scenario for test case
        api_response = await api_instance.get_normalized_scenario(id)
        print("The response of TestCaseScenarioControllerApi->get_normalized_scenario:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->get_normalized_scenario: %s\n" % e)
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

# **get_scenario**
> TestCaseScenarioDto get_scenario(id)

Find scenario for test case

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_scenario_dto import TestCaseScenarioDto
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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find scenario for test case
        api_response = await api_instance.get_scenario(id)
        print("The response of TestCaseScenarioControllerApi->get_scenario:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->get_scenario: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestCaseScenarioDto**](TestCaseScenarioDto.md)

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

# **get_scenario_from_last_run**
> TestCaseScenarioV2Dto get_scenario_from_last_run(id)

Find scenario for test case from last run

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Find scenario for test case from last run
        api_response = await api_instance.get_scenario_from_last_run(id)
        print("The response of TestCaseScenarioControllerApi->get_scenario_from_last_run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->get_scenario_from_last_run: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestCaseScenarioV2Dto**](TestCaseScenarioV2Dto.md)

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

# **migrate_scenario**
> migrate_scenario(id)

Migrate scenario for test case

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 

    try:
        # Migrate scenario for test case
        await api_instance.migrate_scenario(id)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->migrate_scenario: %s\n" % e)
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

# **move**
> NormalizedScenarioDto move(id, scenario_step_move_dto)

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 
    scenario_step_move_dto = src.client.generated.ScenarioStepMoveDto() # ScenarioStepMoveDto | 

    try:
        # Move scenario step
        api_response = await api_instance.move(id, scenario_step_move_dto)
        print("The response of TestCaseScenarioControllerApi->move:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->move: %s\n" % e)
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

# **move1**
> NormalizedScenarioDto move1(id, scenario_step_copy_dto)

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 
    scenario_step_copy_dto = src.client.generated.ScenarioStepCopyDto() # ScenarioStepCopyDto | 

    try:
        # Copy scenario step
        api_response = await api_instance.move1(id, scenario_step_copy_dto)
        print("The response of TestCaseScenarioControllerApi->move1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->move1: %s\n" % e)
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

# **patch_by_id**
> NormalizedScenarioDto patch_by_id(id, scenario_step_patch_dto, with_expected_result=with_expected_result)

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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 
    scenario_step_patch_dto = src.client.generated.ScenarioStepPatchDto() # ScenarioStepPatchDto | 
    with_expected_result = False # bool |  (optional) (default to False)

    try:
        # Patch a specified scenario step
        api_response = await api_instance.patch_by_id(id, scenario_step_patch_dto, with_expected_result=with_expected_result)
        print("The response of TestCaseScenarioControllerApi->patch_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->patch_by_id: %s\n" % e)
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

# **set_test_case_scenario**
> NormalizedScenarioDto set_test_case_scenario(id, test_case_scenario_v2_dto)

Set new type scenario for test case

### Example


```python
import src.client.generated
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
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
    api_instance = src.client.generated.TestCaseScenarioControllerApi(api_client)
    id = 56 # int | 
    test_case_scenario_v2_dto = src.client.generated.TestCaseScenarioV2Dto() # TestCaseScenarioV2Dto | 

    try:
        # Set new type scenario for test case
        api_response = await api_instance.set_test_case_scenario(id, test_case_scenario_v2_dto)
        print("The response of TestCaseScenarioControllerApi->set_test_case_scenario:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseScenarioControllerApi->set_test_case_scenario: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_case_scenario_v2_dto** | [**TestCaseScenarioV2Dto**](TestCaseScenarioV2Dto.md)|  | 

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

