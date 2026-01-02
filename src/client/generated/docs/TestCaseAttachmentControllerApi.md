# src.client.generated.TestCaseAttachmentControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create16**](TestCaseAttachmentControllerApi.md#create16) | **POST** /api/testcase/attachment | Upload new test case attachments
[**delete15**](TestCaseAttachmentControllerApi.md#delete15) | **DELETE** /api/testcase/attachment/{id} | Delete test case attachment
[**find_all13**](TestCaseAttachmentControllerApi.md#find_all13) | **GET** /api/testcase/attachment | Find attachments for test case
[**patch15**](TestCaseAttachmentControllerApi.md#patch15) | **PATCH** /api/testcase/attachment/{id} | Patch test case attachment
[**read_content2**](TestCaseAttachmentControllerApi.md#read_content2) | **GET** /api/testcase/attachment/{id}/content | Get attachment content by id
[**update_content2**](TestCaseAttachmentControllerApi.md#update_content2) | **PUT** /api/testcase/attachment/{id}/content | Update test case attachment content


# **create16**
> List[TestCaseAttachmentRowDto] create16(test_case_id, file)

Upload new test case attachments

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_attachment_row_dto import TestCaseAttachmentRowDto
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
    api_instance = src.client.generated.TestCaseAttachmentControllerApi(api_client)
    test_case_id = 56 # int | 
    file = None # List[bytearray] | 

    try:
        # Upload new test case attachments
        api_response = await api_instance.create16(test_case_id, file)
        print("The response of TestCaseAttachmentControllerApi->create16:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseAttachmentControllerApi->create16: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_id** | **int**|  | 
 **file** | **List[bytearray]**|  | 

### Return type

[**List[TestCaseAttachmentRowDto]**](TestCaseAttachmentRowDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete15**
> delete15(id)

Delete test case attachment

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
    api_instance = src.client.generated.TestCaseAttachmentControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete test case attachment
        await api_instance.delete15(id)
    except Exception as e:
        print("Exception when calling TestCaseAttachmentControllerApi->delete15: %s\n" % e)
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

# **find_all13**
> PageTestCaseAttachmentRowDto find_all13(test_case_id, page=page, size=size, sort=sort)

Find attachments for test case

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_case_attachment_row_dto import PageTestCaseAttachmentRowDto
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
    api_instance = src.client.generated.TestCaseAttachmentControllerApi(api_client)
    test_case_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find attachments for test case
        api_response = await api_instance.find_all13(test_case_id, page=page, size=size, sort=sort)
        print("The response of TestCaseAttachmentControllerApi->find_all13:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseAttachmentControllerApi->find_all13: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestCaseAttachmentRowDto**](PageTestCaseAttachmentRowDto.md)

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

# **patch15**
> TestCaseAttachmentRowDto patch15(id, test_case_attachment_patch_dto)

Patch test case attachment

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_attachment_patch_dto import TestCaseAttachmentPatchDto
from src.client.generated.models.test_case_attachment_row_dto import TestCaseAttachmentRowDto
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
    api_instance = src.client.generated.TestCaseAttachmentControllerApi(api_client)
    id = 56 # int | 
    test_case_attachment_patch_dto = src.client.generated.TestCaseAttachmentPatchDto() # TestCaseAttachmentPatchDto | 

    try:
        # Patch test case attachment
        api_response = await api_instance.patch15(id, test_case_attachment_patch_dto)
        print("The response of TestCaseAttachmentControllerApi->patch15:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseAttachmentControllerApi->patch15: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_case_attachment_patch_dto** | [**TestCaseAttachmentPatchDto**](TestCaseAttachmentPatchDto.md)|  | 

### Return type

[**TestCaseAttachmentRowDto**](TestCaseAttachmentRowDto.md)

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

# **read_content2**
> object read_content2(id, inline=inline)

Get attachment content by id

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
    api_instance = src.client.generated.TestCaseAttachmentControllerApi(api_client)
    id = 56 # int | 
    inline = False # bool |  (optional) (default to False)

    try:
        # Get attachment content by id
        api_response = await api_instance.read_content2(id, inline=inline)
        print("The response of TestCaseAttachmentControllerApi->read_content2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseAttachmentControllerApi->read_content2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **inline** | **bool**|  | [optional] [default to False]

### Return type

**object**

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

# **update_content2**
> TestCaseAttachmentRowDto update_content2(id, file)

Update test case attachment content

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_attachment_row_dto import TestCaseAttachmentRowDto
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
    api_instance = src.client.generated.TestCaseAttachmentControllerApi(api_client)
    id = 56 # int | 
    file = None # bytearray | 

    try:
        # Update test case attachment content
        api_response = await api_instance.update_content2(id, file)
        print("The response of TestCaseAttachmentControllerApi->update_content2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseAttachmentControllerApi->update_content2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **file** | **bytearray**|  | 

### Return type

[**TestCaseAttachmentRowDto**](TestCaseAttachmentRowDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

