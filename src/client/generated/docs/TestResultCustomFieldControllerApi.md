# src.client.generated.TestResultCustomFieldControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_custom_fields_with_values1**](TestResultCustomFieldControllerApi.md#get_custom_fields_with_values1) | **GET** /api/testresult/{testResultId}/cfv | Find custom fields with values for test result
[**set_issues1**](TestResultCustomFieldControllerApi.md#set_issues1) | **POST** /api/testresult/{testResultId}/cfv | Set custom field values to test result


# **get_custom_fields_with_values1**
> List[CustomFieldWithValuesDto] get_custom_fields_with_values1(test_result_id)

Find custom fields with values for test result

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_with_values_dto import CustomFieldWithValuesDto
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
    api_instance = src.client.generated.TestResultCustomFieldControllerApi(api_client)
    test_result_id = 56 # int | 

    try:
        # Find custom fields with values for test result
        api_response = await api_instance.get_custom_fields_with_values1(test_result_id)
        print("The response of TestResultCustomFieldControllerApi->get_custom_fields_with_values1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultCustomFieldControllerApi->get_custom_fields_with_values1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 

### Return type

[**List[CustomFieldWithValuesDto]**](CustomFieldWithValuesDto.md)

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

# **set_issues1**
> List[CustomFieldValueWithCfDto] set_issues1(test_result_id, custom_field_value_with_cf_dto)

Set custom field values to test result

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
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
    api_instance = src.client.generated.TestResultCustomFieldControllerApi(api_client)
    test_result_id = 56 # int | 
    custom_field_value_with_cf_dto = [src.client.generated.CustomFieldValueWithCfDto()] # List[CustomFieldValueWithCfDto] | 

    try:
        # Set custom field values to test result
        api_response = await api_instance.set_issues1(test_result_id, custom_field_value_with_cf_dto)
        print("The response of TestResultCustomFieldControllerApi->set_issues1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultCustomFieldControllerApi->set_issues1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 
 **custom_field_value_with_cf_dto** | [**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md)|  | 

### Return type

[**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md)

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

