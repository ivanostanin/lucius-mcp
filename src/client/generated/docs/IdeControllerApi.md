# src.client.generated.IdeControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**generate_test_code**](IdeControllerApi.md#generate_test_code) | **POST** /api/ide/testcase/{id}/testcode | Generate test code from a test case


# **generate_test_code**
> TestCodeGenerationResponseDto generate_test_code(id, test_code_generation_request_dto)

Generate test code from a test case

### Example


```python
import src.client.generated
from src.client.generated.models.test_code_generation_request_dto import TestCodeGenerationRequestDto
from src.client.generated.models.test_code_generation_response_dto import TestCodeGenerationResponseDto
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
    api_instance = src.client.generated.IdeControllerApi(api_client)
    id = 56 # int | 
    test_code_generation_request_dto = src.client.generated.TestCodeGenerationRequestDto() # TestCodeGenerationRequestDto | 

    try:
        # Generate test code from a test case
        api_response = await api_instance.generate_test_code(id, test_code_generation_request_dto)
        print("The response of IdeControllerApi->generate_test_code:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IdeControllerApi->generate_test_code: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_code_generation_request_dto** | [**TestCodeGenerationRequestDto**](TestCodeGenerationRequestDto.md)|  | 

### Return type

[**TestCodeGenerationResponseDto**](TestCodeGenerationResponseDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Generated test code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

