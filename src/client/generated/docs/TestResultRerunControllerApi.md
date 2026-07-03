# src.client.generated.TestResultRerunControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**retry**](TestResultRerunControllerApi.md#retry) | **POST** /api/testresult/{testResultId}/rerun | Schedule manual rerun for test case
[**retry1**](TestResultRerunControllerApi.md#retry1) | **POST** /api/testresult/{testResultId}/retry | Schedule manual rerun for test case


# **retry**
> IdAndNameOnlyDto retry(test_result_id, test_result_rerun_dto)

Schedule manual rerun for test case

### Example


```python
import src.client.generated
from src.client.generated.models.id_and_name_only_dto import IdAndNameOnlyDto
from src.client.generated.models.test_result_rerun_dto import TestResultRerunDto
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
    api_instance = src.client.generated.TestResultRerunControllerApi(api_client)
    test_result_id = 56 # int | 
    test_result_rerun_dto = src.client.generated.TestResultRerunDto() # TestResultRerunDto | 

    try:
        # Schedule manual rerun for test case
        api_response = await api_instance.retry(test_result_id, test_result_rerun_dto)
        print("The response of TestResultRerunControllerApi->retry:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultRerunControllerApi->retry: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 
 **test_result_rerun_dto** | [**TestResultRerunDto**](TestResultRerunDto.md)|  | 

### Return type

[**IdAndNameOnlyDto**](IdAndNameOnlyDto.md)

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

# **retry1**
> IdAndNameOnlyDto retry1(test_result_id, test_result_rerun_dto)

Schedule manual rerun for test case

### Example


```python
import src.client.generated
from src.client.generated.models.id_and_name_only_dto import IdAndNameOnlyDto
from src.client.generated.models.test_result_rerun_dto import TestResultRerunDto
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
    api_instance = src.client.generated.TestResultRerunControllerApi(api_client)
    test_result_id = 56 # int | 
    test_result_rerun_dto = src.client.generated.TestResultRerunDto() # TestResultRerunDto | 

    try:
        # Schedule manual rerun for test case
        api_response = await api_instance.retry1(test_result_id, test_result_rerun_dto)
        print("The response of TestResultRerunControllerApi->retry1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultRerunControllerApi->retry1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 
 **test_result_rerun_dto** | [**TestResultRerunDto**](TestResultRerunDto.md)|  | 

### Return type

[**IdAndNameOnlyDto**](IdAndNameOnlyDto.md)

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

