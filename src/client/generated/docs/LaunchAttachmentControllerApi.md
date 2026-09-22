# src.client.generated.LaunchAttachmentControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_launch_attachment**](LaunchAttachmentControllerApi.md#create_launch_attachment) | **POST** /api/launch/attachment | Attach one file to a launch
[**list_launch_attachments**](LaunchAttachmentControllerApi.md#list_launch_attachments) | **GET** /api/launch/attachment | List native launch attachments


# **create_launch_attachment**
> List[LaunchAttachmentRowDto] create_launch_attachment(launch_id, file)

Attach one file to a launch

### Example


```python
import src.client.generated
from src.client.generated.models.launch_attachment_row_dto import LaunchAttachmentRowDto
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
    api_instance = src.client.generated.LaunchAttachmentControllerApi(api_client)
    launch_id = 56 # int | 
    file = None # bytes | 

    try:
        # Attach one file to a launch
        api_response = await api_instance.create_launch_attachment(launch_id, file)
        print("The response of LaunchAttachmentControllerApi->create_launch_attachment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LaunchAttachmentControllerApi->create_launch_attachment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **launch_id** | **int**|  | 
 **file** | **bytes**|  | 

### Return type

[**List[LaunchAttachmentRowDto]**](LaunchAttachmentRowDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Created native launch attachment. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_launch_attachments**
> PageLaunchAttachmentRowDto list_launch_attachments(launch_id, page=page, size=size, sort=sort)

List native launch attachments

### Example


```python
import src.client.generated
from src.client.generated.models.page_launch_attachment_row_dto import PageLaunchAttachmentRowDto
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
    api_instance = src.client.generated.LaunchAttachmentControllerApi(api_client)
    launch_id = 56 # int | 
    page = 0 # int |  (optional) (default to 0)
    size = 10 # int |  (optional) (default to 10)
    sort = ['sort_example'] # List[str] |  (optional)

    try:
        # List native launch attachments
        api_response = await api_instance.list_launch_attachments(launch_id, page=page, size=size, sort=sort)
        print("The response of LaunchAttachmentControllerApi->list_launch_attachments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LaunchAttachmentControllerApi->list_launch_attachments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **launch_id** | **int**|  | 
 **page** | **int**|  | [optional] [default to 0]
 **size** | **int**|  | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**PageLaunchAttachmentRowDto**](PageLaunchAttachmentRowDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Native launch attachment page. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

