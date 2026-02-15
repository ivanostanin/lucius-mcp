# src.client.generated.TestCaseTreeControllerV2Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_group**](TestCaseTreeControllerV2Api.md#add_group) | **POST** /api/v2/project/{projectId}/test-case/tree/group | Add a new group to the specified tree
[**add_leaf**](TestCaseTreeControllerV2Api.md#add_leaf) | **POST** /api/v2/project/{projectId}/test-case/tree/leaf | Add a new leaf to the specified tree
[**delete_group**](TestCaseTreeControllerV2Api.md#delete_group) | **DELETE** /api/v2/project/{projectId}/test-case/tree/group/{groupId} | Delete the specified group
[**get_tree_node**](TestCaseTreeControllerV2Api.md#get_tree_node) | **GET** /api/v2/project/{projectId}/test-case/tree/tree-node | Get test cases as a tree structure (AQL)
[**rename_group**](TestCaseTreeControllerV2Api.md#rename_group) | **PUT** /api/v2/project/{projectId}/test-case/tree/group/{groupId}/name | Rename the specified group
[**rename_leaf**](TestCaseTreeControllerV2Api.md#rename_leaf) | **PUT** /api/v2/project/{projectId}/test-case/tree/leaf/{leafId}/name | Rename the specified leaf
[**suggest1**](TestCaseTreeControllerV2Api.md#suggest1) | **GET** /api/v2/project/{projectId}/test-case/tree/suggest | Tree groups suggest
[**upsert**](TestCaseTreeControllerV2Api.md#upsert) | **PUT** /api/v2/project/{projectId}/test-case/tree/group | Add a new group to the specified tree and return group if it exists


# **add_group**
> TestCaseLightTreeNodeDto add_group(project_id, tree_id, test_case_tree_group_add_dto, parent_node_id=parent_node_id)

Add a new group to the specified tree

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto
from src.client.generated.models.test_case_tree_group_add_dto import TestCaseTreeGroupAddDto
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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    tree_id = 56 # int | 
    test_case_tree_group_add_dto = src.client.generated.TestCaseTreeGroupAddDto() # TestCaseTreeGroupAddDto | 
    parent_node_id = 56 # int |  (optional)

    try:
        # Add a new group to the specified tree
        api_response = await api_instance.add_group(project_id, tree_id, test_case_tree_group_add_dto, parent_node_id=parent_node_id)
        print("The response of TestCaseTreeControllerV2Api->add_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->add_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **tree_id** | **int**|  | 
 **test_case_tree_group_add_dto** | [**TestCaseTreeGroupAddDto**](TestCaseTreeGroupAddDto.md)|  | 
 **parent_node_id** | **int**|  | [optional] 

### Return type

[**TestCaseLightTreeNodeDto**](TestCaseLightTreeNodeDto.md)

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

# **add_leaf**
> TestCaseTreeLeafDtoV2 add_leaf(project_id, tree_id, test_case_tree_leaf_add_dto, node_id=node_id)

Add a new leaf to the specified tree

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_tree_leaf_add_dto import TestCaseTreeLeafAddDto
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    tree_id = 56 # int | 
    test_case_tree_leaf_add_dto = src.client.generated.TestCaseTreeLeafAddDto() # TestCaseTreeLeafAddDto | 
    node_id = 56 # int |  (optional)

    try:
        # Add a new leaf to the specified tree
        api_response = await api_instance.add_leaf(project_id, tree_id, test_case_tree_leaf_add_dto, node_id=node_id)
        print("The response of TestCaseTreeControllerV2Api->add_leaf:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->add_leaf: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **tree_id** | **int**|  | 
 **test_case_tree_leaf_add_dto** | [**TestCaseTreeLeafAddDto**](TestCaseTreeLeafAddDto.md)|  | 
 **node_id** | **int**|  | [optional] 

### Return type

[**TestCaseTreeLeafDtoV2**](TestCaseTreeLeafDtoV2.md)

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

# **delete_group**
> delete_group(project_id, group_id)

Delete the specified group

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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    group_id = 56 # int | 

    try:
        # Delete the specified group
        await api_instance.delete_group(project_id, group_id)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->delete_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **group_id** | **int**|  | 

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

# **get_tree_node**
> TestCaseFullTreeNodeDto get_tree_node(project_id, tree_id, parent_node_id=parent_node_id, search=search, filter_id=filter_id, page=page, size=size, sort=sort, query=query, base_aql=base_aql)

Get test cases as a tree structure (AQL)

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_full_tree_node_dto import TestCaseFullTreeNodeDto
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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    tree_id = 56 # int | 
    parent_node_id = 56 # int |  (optional)
    search = 'search_example' # str |  (optional)
    filter_id = 56 # int |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 100 # int | The size of the page to be returned (optional) (default to 100)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])
    query = 'query_example' # str |  (optional)
    base_aql = 'base_aql_example' # str |  (optional)

    try:
        # Get test cases as a tree structure (AQL)
        api_response = await api_instance.get_tree_node(project_id, tree_id, parent_node_id=parent_node_id, search=search, filter_id=filter_id, page=page, size=size, sort=sort, query=query, base_aql=base_aql)
        print("The response of TestCaseTreeControllerV2Api->get_tree_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->get_tree_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **tree_id** | **int**|  | 
 **parent_node_id** | **int**|  | [optional] 
 **search** | **str**|  | [optional] 
 **filter_id** | **int**|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 100]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]
 **query** | **str**|  | [optional] 
 **base_aql** | **str**|  | [optional] 

### Return type

[**TestCaseFullTreeNodeDto**](TestCaseFullTreeNodeDto.md)

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

# **rename_group**
> TestCaseLightTreeNodeDto rename_group(project_id, group_id, test_case_tree_group_rename_dto)

Rename the specified group

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto
from src.client.generated.models.test_case_tree_group_rename_dto import TestCaseTreeGroupRenameDto
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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    group_id = 56 # int | 
    test_case_tree_group_rename_dto = src.client.generated.TestCaseTreeGroupRenameDto() # TestCaseTreeGroupRenameDto | 

    try:
        # Rename the specified group
        api_response = await api_instance.rename_group(project_id, group_id, test_case_tree_group_rename_dto)
        print("The response of TestCaseTreeControllerV2Api->rename_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->rename_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **group_id** | **int**|  | 
 **test_case_tree_group_rename_dto** | [**TestCaseTreeGroupRenameDto**](TestCaseTreeGroupRenameDto.md)|  | 

### Return type

[**TestCaseLightTreeNodeDto**](TestCaseLightTreeNodeDto.md)

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

# **rename_leaf**
> TestCaseTreeLeafDtoV2 rename_leaf(project_id, leaf_id, test_case_tree_leaf_rename_dto)

Rename the specified leaf

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
from src.client.generated.models.test_case_tree_leaf_rename_dto import TestCaseTreeLeafRenameDto
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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    leaf_id = 56 # int | 
    test_case_tree_leaf_rename_dto = src.client.generated.TestCaseTreeLeafRenameDto() # TestCaseTreeLeafRenameDto | 

    try:
        # Rename the specified leaf
        api_response = await api_instance.rename_leaf(project_id, leaf_id, test_case_tree_leaf_rename_dto)
        print("The response of TestCaseTreeControllerV2Api->rename_leaf:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->rename_leaf: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **leaf_id** | **int**|  | 
 **test_case_tree_leaf_rename_dto** | [**TestCaseTreeLeafRenameDto**](TestCaseTreeLeafRenameDto.md)|  | 

### Return type

[**TestCaseTreeLeafDtoV2**](TestCaseTreeLeafDtoV2.md)

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

# **suggest1**
> PageIdAndNameOnlyDto suggest1(project_id, query=query, tree_id=tree_id, path=path, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)

Tree groups suggest

### Example


```python
import src.client.generated
from src.client.generated.models.page_id_and_name_only_dto import PageIdAndNameOnlyDto
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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    query = 'query_example' # str |  (optional)
    tree_id = 56 # int |  (optional)
    path = [] # List[int] |  (optional) (default to [])
    id = [56] # List[int] |  (optional)
    ignore_id = [56] # List[int] |  (optional)
    page = 0 # int | Zero-based page index (0..N) (optional) (default to 0)
    size = 10 # int | The size of the page to be returned (optional) (default to 10)
    sort = [name,ASC] # List[str] | Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. (optional) (default to [name,ASC])

    try:
        # Tree groups suggest
        api_response = await api_instance.suggest1(project_id, query=query, tree_id=tree_id, path=path, id=id, ignore_id=ignore_id, page=page, size=size, sort=sort)
        print("The response of TestCaseTreeControllerV2Api->suggest1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->suggest1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **query** | **str**|  | [optional] 
 **tree_id** | **int**|  | [optional] 
 **path** | [**List[int]**](int.md)|  | [optional] [default to []]
 **id** | [**List[int]**](int.md)|  | [optional] 
 **ignore_id** | [**List[int]**](int.md)|  | [optional] 
 **page** | **int**| Zero-based page index (0..N) | [optional] [default to 0]
 **size** | **int**| The size of the page to be returned | [optional] [default to 10]
 **sort** | [**List[str]**](str.md)| Sorting criteria in the format: property(,asc|desc). Default sort order is ascending. Multiple sort criteria are supported. | [optional] [default to [name,ASC]]

### Return type

[**PageIdAndNameOnlyDto**](PageIdAndNameOnlyDto.md)

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

# **upsert**
> TestCaseLightTreeNodeDto upsert(project_id, tree_id, test_case_tree_group_add_dto, parent_node_id=parent_node_id)

Add a new group to the specified tree and return group if it exists

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto
from src.client.generated.models.test_case_tree_group_add_dto import TestCaseTreeGroupAddDto
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
    api_instance = src.client.generated.TestCaseTreeControllerV2Api(api_client)
    project_id = 56 # int | 
    tree_id = 56 # int | 
    test_case_tree_group_add_dto = src.client.generated.TestCaseTreeGroupAddDto() # TestCaseTreeGroupAddDto | 
    parent_node_id = 56 # int |  (optional)

    try:
        # Add a new group to the specified tree and return group if it exists
        api_response = await api_instance.upsert(project_id, tree_id, test_case_tree_group_add_dto, parent_node_id=parent_node_id)
        print("The response of TestCaseTreeControllerV2Api->upsert:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTreeControllerV2Api->upsert: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **tree_id** | **int**|  | 
 **test_case_tree_group_add_dto** | [**TestCaseTreeGroupAddDto**](TestCaseTreeGroupAddDto.md)|  | 
 **parent_node_id** | **int**|  | [optional] 

### Return type

[**TestCaseLightTreeNodeDto**](TestCaseLightTreeNodeDto.md)

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

