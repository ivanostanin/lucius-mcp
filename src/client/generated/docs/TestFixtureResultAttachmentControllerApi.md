# src.client.generated.TestFixtureResultAttachmentControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create11**](TestFixtureResultAttachmentControllerApi.md#create11) | **POST** /api/testfixtureresult/attachment | 
[**delete11**](TestFixtureResultAttachmentControllerApi.md#delete11) | **DELETE** /api/testfixtureresult/attachment/{id} | 
[**find_all9**](TestFixtureResultAttachmentControllerApi.md#find_all9) | **GET** /api/testfixtureresult/attachment | 
[**patch11**](TestFixtureResultAttachmentControllerApi.md#patch11) | **PATCH** /api/testfixtureresult/attachment/{id} | 
[**read_content1**](TestFixtureResultAttachmentControllerApi.md#read_content1) | **GET** /api/testfixtureresult/attachment/{id}/content | 
[**update_content1**](TestFixtureResultAttachmentControllerApi.md#update_content1) | **PUT** /api/testfixtureresult/attachment/{id}/content | 


# **create11**
> List[TestFixtureResultAttachmentRowDto] create11(tfr_id, file)

### Example


```python
import src.client.generated
from src.client.generated.models.test_fixture_result_attachment_row_dto import TestFixtureResultAttachmentRowDto
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
    api_instance = src.client.generated.TestFixtureResultAttachmentControllerApi(api_client)
    tfr_id = 56 # int | 
    file = None # List[bytes] | 

    try:
        api_response = await api_instance.create11(tfr_id, file)
        print("The response of TestFixtureResultAttachmentControllerApi->create11:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestFixtureResultAttachmentControllerApi->create11: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tfr_id** | **int**|  | 
 **file** | **List[bytes]**|  | 

### Return type

[**List[TestFixtureResultAttachmentRowDto]**](TestFixtureResultAttachmentRowDto.md)

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

# **delete11**
> delete11(id)

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
    api_instance = src.client.generated.TestFixtureResultAttachmentControllerApi(api_client)
    id = 56 # int | 

    try:
        await api_instance.delete11(id)
    except Exception as e:
        print("Exception when calling TestFixtureResultAttachmentControllerApi->delete11: %s\n" % e)
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

# **find_all9**
> PageTestFixtureResultAttachmentRowDto find_all9(tfr_id, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_test_fixture_result_attachment_row_dto import PageTestFixtureResultAttachmentRowDto
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
    api_instance = src.client.generated.TestFixtureResultAttachmentControllerApi(api_client)
    tfr_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.find_all9(tfr_id, page=page, size=size, sort=sort)
        print("The response of TestFixtureResultAttachmentControllerApi->find_all9:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestFixtureResultAttachmentControllerApi->find_all9: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tfr_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTestFixtureResultAttachmentRowDto**](PageTestFixtureResultAttachmentRowDto.md)

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

# **patch11**
> TestFixtureResultAttachmentRowDto patch11(id, test_fixture_result_attachment_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.test_fixture_result_attachment_patch_dto import TestFixtureResultAttachmentPatchDto
from src.client.generated.models.test_fixture_result_attachment_row_dto import TestFixtureResultAttachmentRowDto
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
    api_instance = src.client.generated.TestFixtureResultAttachmentControllerApi(api_client)
    id = 56 # int | 
    test_fixture_result_attachment_patch_dto = src.client.generated.TestFixtureResultAttachmentPatchDto() # TestFixtureResultAttachmentPatchDto | 

    try:
        api_response = await api_instance.patch11(id, test_fixture_result_attachment_patch_dto)
        print("The response of TestFixtureResultAttachmentControllerApi->patch11:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestFixtureResultAttachmentControllerApi->patch11: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **test_fixture_result_attachment_patch_dto** | [**TestFixtureResultAttachmentPatchDto**](TestFixtureResultAttachmentPatchDto.md)|  | 

### Return type

[**TestFixtureResultAttachmentRowDto**](TestFixtureResultAttachmentRowDto.md)

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

# **read_content1**
> object read_content1(id, inline=inline)

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
    api_instance = src.client.generated.TestFixtureResultAttachmentControllerApi(api_client)
    id = 56 # int | 
    inline = False # bool |  (optional) (default to False)

    try:
        api_response = await api_instance.read_content1(id, inline=inline)
        print("The response of TestFixtureResultAttachmentControllerApi->read_content1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestFixtureResultAttachmentControllerApi->read_content1: %s\n" % e)
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

# **update_content1**
> TestFixtureResultAttachmentRowDto update_content1(id, file)

### Example


```python
import src.client.generated
from src.client.generated.models.test_fixture_result_attachment_row_dto import TestFixtureResultAttachmentRowDto
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
    api_instance = src.client.generated.TestFixtureResultAttachmentControllerApi(api_client)
    id = 56 # int | 
    file = None # bytes | 

    try:
        api_response = await api_instance.update_content1(id, file)
        print("The response of TestFixtureResultAttachmentControllerApi->update_content1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestFixtureResultAttachmentControllerApi->update_content1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **file** | **bytes**|  | 

### Return type

[**TestFixtureResultAttachmentRowDto**](TestFixtureResultAttachmentRowDto.md)

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

