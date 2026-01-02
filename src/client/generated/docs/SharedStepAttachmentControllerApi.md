# src.client.generated.SharedStepAttachmentControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create21**](SharedStepAttachmentControllerApi.md#create21) | **POST** /api/sharedstep/attachment | Upload new shared step attachments
[**delete19**](SharedStepAttachmentControllerApi.md#delete19) | **DELETE** /api/sharedstep/attachment/{id} | Delete shared step attachment
[**find_all17**](SharedStepAttachmentControllerApi.md#find_all17) | **GET** /api/sharedstep/attachment | Find attachments for shared step
[**patch19**](SharedStepAttachmentControllerApi.md#patch19) | **PATCH** /api/sharedstep/attachment/{id} | Patch shared step attachment
[**read_content3**](SharedStepAttachmentControllerApi.md#read_content3) | **GET** /api/sharedstep/attachment/{id}/content | Get attachment content by id
[**update_content3**](SharedStepAttachmentControllerApi.md#update_content3) | **PUT** /api/sharedstep/attachment/{id}/content | Update shared step attachment content


# **create21**
> List[SharedStepAttachmentRowDto] create21(shared_step_id, file)

Upload new shared step attachments

### Example


```python
import src.client.generated
from src.client.generated.models.shared_step_attachment_row_dto import SharedStepAttachmentRowDto
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
    api_instance = src.client.generated.SharedStepAttachmentControllerApi(api_client)
    shared_step_id = 56 # int | 
    file = None # List[bytearray] | 

    try:
        # Upload new shared step attachments
        api_response = await api_instance.create21(shared_step_id, file)
        print("The response of SharedStepAttachmentControllerApi->create21:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepAttachmentControllerApi->create21: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shared_step_id** | **int**|  | 
 **file** | **List[bytearray]**|  | 

### Return type

[**List[SharedStepAttachmentRowDto]**](SharedStepAttachmentRowDto.md)

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

# **delete19**
> delete19(id)

Delete shared step attachment

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
    api_instance = src.client.generated.SharedStepAttachmentControllerApi(api_client)
    id = 56 # int | 

    try:
        # Delete shared step attachment
        await api_instance.delete19(id)
    except Exception as e:
        print("Exception when calling SharedStepAttachmentControllerApi->delete19: %s\n" % e)
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

# **find_all17**
> PageSharedStepAttachmentRowDto find_all17(shared_step_id, page=page, size=size, sort=sort)

Find attachments for shared step

### Example


```python
import src.client.generated
from src.client.generated.models.page_shared_step_attachment_row_dto import PageSharedStepAttachmentRowDto
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
    api_instance = src.client.generated.SharedStepAttachmentControllerApi(api_client)
    shared_step_id = 56 # int | 
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Find attachments for shared step
        api_response = await api_instance.find_all17(shared_step_id, page=page, size=size, sort=sort)
        print("The response of SharedStepAttachmentControllerApi->find_all17:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepAttachmentControllerApi->find_all17: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shared_step_id** | **int**|  | 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageSharedStepAttachmentRowDto**](PageSharedStepAttachmentRowDto.md)

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

# **patch19**
> SharedStepAttachmentRowDto patch19(id, shared_step_attachment_patch_dto)

Patch shared step attachment

### Example


```python
import src.client.generated
from src.client.generated.models.shared_step_attachment_patch_dto import SharedStepAttachmentPatchDto
from src.client.generated.models.shared_step_attachment_row_dto import SharedStepAttachmentRowDto
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
    api_instance = src.client.generated.SharedStepAttachmentControllerApi(api_client)
    id = 56 # int | 
    shared_step_attachment_patch_dto = src.client.generated.SharedStepAttachmentPatchDto() # SharedStepAttachmentPatchDto | 

    try:
        # Patch shared step attachment
        api_response = await api_instance.patch19(id, shared_step_attachment_patch_dto)
        print("The response of SharedStepAttachmentControllerApi->patch19:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepAttachmentControllerApi->patch19: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **shared_step_attachment_patch_dto** | [**SharedStepAttachmentPatchDto**](SharedStepAttachmentPatchDto.md)|  | 

### Return type

[**SharedStepAttachmentRowDto**](SharedStepAttachmentRowDto.md)

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

# **read_content3**
> object read_content3(id, inline=inline)

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
    api_instance = src.client.generated.SharedStepAttachmentControllerApi(api_client)
    id = 56 # int | 
    inline = False # bool |  (optional) (default to False)

    try:
        # Get attachment content by id
        api_response = await api_instance.read_content3(id, inline=inline)
        print("The response of SharedStepAttachmentControllerApi->read_content3:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepAttachmentControllerApi->read_content3: %s\n" % e)
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

# **update_content3**
> SharedStepAttachmentRowDto update_content3(id, file)

Update shared step attachment content

### Example


```python
import src.client.generated
from src.client.generated.models.shared_step_attachment_row_dto import SharedStepAttachmentRowDto
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
    api_instance = src.client.generated.SharedStepAttachmentControllerApi(api_client)
    id = 56 # int | 
    file = None # bytearray | 

    try:
        # Update shared step attachment content
        api_response = await api_instance.update_content3(id, file)
        print("The response of SharedStepAttachmentControllerApi->update_content3:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharedStepAttachmentControllerApi->update_content3: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **file** | **bytearray**|  | 

### Return type

[**SharedStepAttachmentRowDto**](SharedStepAttachmentRowDto.md)

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

