# src.client.generated.TreeControllerV2Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**find_all48**](TreeControllerV2Api.md#find_all48) | **GET** /api/v2/tree | 
[**find_one38**](TreeControllerV2Api.md#find_one38) | **GET** /api/v2/tree/{id} | 


# **find_all48**
> PageTreeDtoV2 find_all48(project_id, with_archived=with_archived, page=page, size=size, sort=sort)

### Example


```python
import src.client.generated
from src.client.generated.models.page_tree_dto_v2 import PageTreeDtoV2
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
    api_instance = src.client.generated.TreeControllerV2Api(api_client)
    project_id = 56 # int | 
    with_archived = False # bool |  (optional) (default to False)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        api_response = await api_instance.find_all48(project_id, with_archived=with_archived, page=page, size=size, sort=sort)
        print("The response of TreeControllerV2Api->find_all48:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TreeControllerV2Api->find_all48: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **with_archived** | **bool**|  | [optional] [default to False]
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageTreeDtoV2**](PageTreeDtoV2.md)

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

# **find_one38**
> TreeDtoV2 find_one38(id, with_archived=with_archived)

### Example


```python
import src.client.generated
from src.client.generated.models.tree_dto_v2 import TreeDtoV2
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
    api_instance = src.client.generated.TreeControllerV2Api(api_client)
    id = 56 # int | 
    with_archived = False # bool |  (optional) (default to False)

    try:
        api_response = await api_instance.find_one38(id, with_archived=with_archived)
        print("The response of TreeControllerV2Api->find_one38:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TreeControllerV2Api->find_one38: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **with_archived** | **bool**|  | [optional] [default to False]

### Return type

[**TreeDtoV2**](TreeDtoV2.md)

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

