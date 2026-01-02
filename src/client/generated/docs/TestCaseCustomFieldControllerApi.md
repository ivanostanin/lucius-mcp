# src.client.generated.TestCaseCustomFieldControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_custom_fields_with_values2**](TestCaseCustomFieldControllerApi.md#get_custom_fields_with_values2) | **POST** /api/testcase/cfv | Find custom fields with values for test cases
[**get_custom_fields_with_values3**](TestCaseCustomFieldControllerApi.md#get_custom_fields_with_values3) | **GET** /api/testcase/{testCaseId}/cfv | Find custom fields with values for test case
[**update_cfvs_of_test_case**](TestCaseCustomFieldControllerApi.md#update_cfvs_of_test_case) | **PATCH** /api/testcase/{testCaseId}/cfv | Update custom field values of test case


# **get_custom_fields_with_values2**
> List[CustomFieldProjectWithValuesDto] get_custom_fields_with_values2(test_case_tree_selection_dto=test_case_tree_selection_dto)

Find custom fields with values for test cases

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_project_with_values_dto import CustomFieldProjectWithValuesDto
from src.client.generated.models.test_case_tree_selection_dto import TestCaseTreeSelectionDto
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
    api_instance = src.client.generated.TestCaseCustomFieldControllerApi(api_client)
    test_case_tree_selection_dto = src.client.generated.TestCaseTreeSelectionDto() # TestCaseTreeSelectionDto |  (optional)

    try:
        # Find custom fields with values for test cases
        api_response = await api_instance.get_custom_fields_with_values2(test_case_tree_selection_dto=test_case_tree_selection_dto)
        print("The response of TestCaseCustomFieldControllerApi->get_custom_fields_with_values2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseCustomFieldControllerApi->get_custom_fields_with_values2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_tree_selection_dto** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md)|  | [optional] 

### Return type

[**List[CustomFieldProjectWithValuesDto]**](CustomFieldProjectWithValuesDto.md)

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

# **get_custom_fields_with_values3**
> List[CustomFieldProjectWithValuesDto] get_custom_fields_with_values3(test_case_id, project_id)

Find custom fields with values for test case

### Example


```python
import src.client.generated
from src.client.generated.models.custom_field_project_with_values_dto import CustomFieldProjectWithValuesDto
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
    api_instance = src.client.generated.TestCaseCustomFieldControllerApi(api_client)
    test_case_id = 56 # int | 
    project_id = 56 # int | 

    try:
        # Find custom fields with values for test case
        api_response = await api_instance.get_custom_fields_with_values3(test_case_id, project_id)
        print("The response of TestCaseCustomFieldControllerApi->get_custom_fields_with_values3:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseCustomFieldControllerApi->get_custom_fields_with_values3: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_id** | **int**|  | 
 **project_id** | **int**|  | 

### Return type

[**List[CustomFieldProjectWithValuesDto]**](CustomFieldProjectWithValuesDto.md)

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

# **update_cfvs_of_test_case**
> update_cfvs_of_test_case(test_case_id, custom_field_with_values_dto)

Update custom field values of test case

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
    api_instance = src.client.generated.TestCaseCustomFieldControllerApi(api_client)
    test_case_id = 56 # int | 
    custom_field_with_values_dto = [src.client.generated.CustomFieldWithValuesDto()] # List[CustomFieldWithValuesDto] | 

    try:
        # Update custom field values of test case
        await api_instance.update_cfvs_of_test_case(test_case_id, custom_field_with_values_dto)
    except Exception as e:
        print("Exception when calling TestCaseCustomFieldControllerApi->update_cfvs_of_test_case: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_id** | **int**|  | 
 **custom_field_with_values_dto** | [**List[CustomFieldWithValuesDto]**](CustomFieldWithValuesDto.md)|  | 

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

