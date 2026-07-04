# src.client.generated.TestResultAttachmentControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create6**](TestResultAttachmentControllerApi.md#create6) | **POST** /api/testresult/attachment | 
[**delete6**](TestResultAttachmentControllerApi.md#delete6) | **DELETE** /api/testresult/attachment/{id} | 
[**find_all5**](TestResultAttachmentControllerApi.md#find_all5) | **GET** /api/testresult/attachment | 
[**patch6**](TestResultAttachmentControllerApi.md#patch6) | **PATCH** /api/testresult/attachment/{id} | 
[**read_content**](TestResultAttachmentControllerApi.md#read_content) | **GET** /api/testresult/attachment/{id}/content | 
[**update_content**](TestResultAttachmentControllerApi.md#update_content) | **PUT** /api/testresult/attachment/{id}/content | 


# **create6**
> List[TestResultAttachmentRowDto] create6(test_result_id, file)

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
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
    api_instance = src.client.generated.TestResultAttachmentControllerApi(api_client)
    test_result_id = 56 # int | 
    file = None # List[bytes] | 

    try:
        api_response = await api_instance.create6(test_result_id, file)
        print("The response of TestResultAttachmentControllerApi->create6:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultAttachmentControllerApi->create6: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 
 **file** | **List[bytes]**|  | 

### Return type

[**List[TestResultAttachmentRowDto]**](TestResultAttachmentRowDto.md)

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

# **delete6**
> delete6(id)

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
    api_instance = src.client.generated.TestResultAttachmentControllerApi(api_client)
    id = 56 # int | 

    try:
        await api_instance.delete6(id)
    except Exception as e:
        print("Exception when calling TestResultAttachmentControllerApi->delete6: %s\n" % e)
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

# **find_all5**
> PageTestResultAttachmentRowDto find_all5(test_result_id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_result_attachment_row_dto import PageTestResultAttachmentRowDto
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
    api_instance = src.client.generated.TestResultAttachmentControllerApi(api_client)
    test_result_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.find_all5(test_result_id, page=page, size=size, sort=sort)
        print("The response of TestResultAttachmentControllerApi->find_all5:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultAttachmentControllerApi->find_all5: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_result_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestResultAttachmentRowDto**](PageTestResultAttachmentRowDto.md)

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

# **patch6**
> TestResultAttachmentRowDto patch6(id, test_result_attachment_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_attachment_patch_dto import TestResultAttachmentPatchDto
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
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
    api_instance = src.client.generated.TestResultAttachmentControllerApi(api_client)
    id = 56 # int | 
    test_result_attachment_patch_dto = src.client.generated.TestResultAttachmentPatchDto() # TestResultAttachmentPatchDto | 

    try:
        api_response = await api_instance.patch6(id, test_result_attachment_patch_dto)
        print("The response of TestResultAttachmentControllerApi->patch6:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultAttachmentControllerApi->patch6: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_result_attachment_patch_dto** | [**TestResultAttachmentPatchDto**](TestResultAttachmentPatchDto.md)|  | 

### Return type

[**TestResultAttachmentRowDto**](TestResultAttachmentRowDto.md)

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

# **read_content**
> object read_content(id, inline=inline)

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
    api_instance = src.client.generated.TestResultAttachmentControllerApi(api_client)
    id = 56 # int | 
    inline = False # bool |  (optional) (default to False)

    try:
        api_response = await api_instance.read_content(id, inline=inline)
        print("The response of TestResultAttachmentControllerApi->read_content:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultAttachmentControllerApi->read_content: %s\n" % e)
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

# **update_content**
> TestResultAttachmentRowDto update_content(id, file)

### Example


```python
import src.client.generated
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
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
    api_instance = src.client.generated.TestResultAttachmentControllerApi(api_client)
    id = 56 # int | 
    file = None # bytes | 

    try:
        api_response = await api_instance.update_content(id, file)
        print("The response of TestResultAttachmentControllerApi->update_content:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestResultAttachmentControllerApi->update_content: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **file** | **bytes**|  | 

### Return type

[**TestResultAttachmentRowDto**](TestResultAttachmentRowDto.md)

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

