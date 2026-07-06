# src.client.generated.TestResultRunControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**assign**](TestResultRunControllerApi.md#assign) | **POST** /api/testresult/{id}/assign | Assign test result
[**resolve1**](TestResultRunControllerApi.md#resolve1) | **POST** /api/testresult/{id}/resolve | Resolve test result


# **assign**
> TestResultRowDto assign(id, assign_request_dto)

Assign test result

### Example


```python
import src.client.generated
from src.client.generated.models.assign_request_dto import AssignRequestDto
from src.client.generated.models.test_result_row_dto import TestResultRowDto
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
    api_instance = src.client.generated.TestResultRunControllerApi(api_client)
    id = 56 # int | 
    assign_request_dto = src.client.generated.AssignRequestDto() # AssignRequestDto | 

    try:
        # Assign test result
        api_response = await api_instance.assign(id, assign_request_dto)
        print("The response of TestResultRunControllerApi->assign:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultRunControllerApi->assign: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **assign_request_dto** | [**AssignRequestDto**](AssignRequestDto.md)|  | 

### Return type

[**TestResultRowDto**](TestResultRowDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resolve1**
> TestResultRowDto resolve1(id, resolve_request_v2_dto)

Resolve test result

### Example


```python
import src.client.generated
from src.client.generated.models.resolve_request_v2_dto import ResolveRequestV2Dto
from src.client.generated.models.test_result_row_dto import TestResultRowDto
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
    api_instance = src.client.generated.TestResultRunControllerApi(api_client)
    id = 56 # int | 
    resolve_request_v2_dto = src.client.generated.ResolveRequestV2Dto() # ResolveRequestV2Dto | 

    try:
        # Resolve test result
        api_response = await api_instance.resolve1(id, resolve_request_v2_dto)
        print("The response of TestResultRunControllerApi->resolve1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultRunControllerApi->resolve1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **resolve_request_v2_dto** | [**ResolveRequestV2Dto**](ResolveRequestV2Dto.md)|  | 

### Return type

[**TestResultRowDto**](TestResultRowDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

