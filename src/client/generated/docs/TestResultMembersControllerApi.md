# src.client.generated.TestResultMembersControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_members**](TestResultMembersControllerApi.md#get_members) | **GET** /api/testresult/{testResultId}/members | Find user roles for test result
[**set_members**](TestResultMembersControllerApi.md#set_members) | **POST** /api/testresult/{testResultId}/members | Set user roles for test result


# **get_members**
> List[MemberDto] get_members(test_result_id)

Find user roles for test result

### Example


```python
import src.client.generated
from src.client.generated.models.member_dto import MemberDto
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
    api_instance = src.client.generated.TestResultMembersControllerApi(api_client)
    test_result_id = 56 # int | 

    try:
        # Find user roles for test result
        api_response = await api_instance.get_members(test_result_id)
        print("The response of TestResultMembersControllerApi->get_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultMembersControllerApi->get_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 

### Return type

[**List[MemberDto]**](MemberDto.md)

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

# **set_members**
> List[MemberDto] set_members(test_result_id, member_dto)

Set user roles for test result

### Example


```python
import src.client.generated
from src.client.generated.models.member_dto import MemberDto
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
    api_instance = src.client.generated.TestResultMembersControllerApi(api_client)
    test_result_id = 56 # int | 
    member_dto = [src.client.generated.MemberDto()] # List[MemberDto] | 

    try:
        # Set user roles for test result
        api_response = await api_instance.set_members(test_result_id, member_dto)
        print("The response of TestResultMembersControllerApi->set_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultMembersControllerApi->set_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 
 **member_dto** | [**List[MemberDto]**](MemberDto.md)|  | 

### Return type

[**List[MemberDto]**](MemberDto.md)

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

