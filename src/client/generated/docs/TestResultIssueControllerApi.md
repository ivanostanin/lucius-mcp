# src.client.generated.TestResultIssueControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_issues**](TestResultIssueControllerApi.md#get_issues) | **GET** /api/testresult/{testResultId}/issue | Find issues for test result
[**set_issues**](TestResultIssueControllerApi.md#set_issues) | **POST** /api/testresult/{testResultId}/issue | Set issues to test result


# **get_issues**
> List[IssueDto] get_issues(test_result_id)

Find issues for test result

### Example


```python
import src.client.generated
from src.client.generated.models.issue_dto import IssueDto
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
    api_instance = src.client.generated.TestResultIssueControllerApi(api_client)
    test_result_id = 56 # int | 

    try:
        # Find issues for test result
        api_response = await api_instance.get_issues(test_result_id)
        print("The response of TestResultIssueControllerApi->get_issues:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultIssueControllerApi->get_issues: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 

### Return type

[**List[IssueDto]**](IssueDto.md)

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

# **set_issues**
> List[IssueDto] set_issues(test_result_id, issue_dto)

Set issues to test result

### Example


```python
import src.client.generated
from src.client.generated.models.issue_dto import IssueDto
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
    api_instance = src.client.generated.TestResultIssueControllerApi(api_client)
    test_result_id = 56 # int | 
    issue_dto = [src.client.generated.IssueDto()] # List[IssueDto] | 

    try:
        # Set issues to test result
        api_response = await api_instance.set_issues(test_result_id, issue_dto)
        print("The response of TestResultIssueControllerApi->set_issues:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultIssueControllerApi->set_issues: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 
 **issue_dto** | [**List[IssueDto]**](IssueDto.md)|  | 

### Return type

[**List[IssueDto]**](IssueDto.md)

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

