# src.client.generated.DefectMatcherControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create46**](DefectMatcherControllerApi.md#create46) | **POST** /api/defect/matcher | 
[**delete38**](DefectMatcherControllerApi.md#delete38) | **DELETE** /api/defect/matcher/{id} | 
[**patch43**](DefectMatcherControllerApi.md#patch43) | **PATCH** /api/defect/matcher/{id} | 


# **create46**
> DefectMatcherDto create46(defect_matcher_create_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_matcher_create_dto import DefectMatcherCreateDto
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto
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
    api_instance = src.client.generated.DefectMatcherControllerApi(api_client)
    defect_matcher_create_dto = src.client.generated.DefectMatcherCreateDto() # DefectMatcherCreateDto | 

    try:
        api_response = await api_instance.create46(defect_matcher_create_dto)
        print("The response of DefectMatcherControllerApi->create46:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectMatcherControllerApi->create46: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **defect_matcher_create_dto** | [**DefectMatcherCreateDto**](DefectMatcherCreateDto.md)|  | 

### Return type

[**DefectMatcherDto**](DefectMatcherDto.md)

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

# **delete38**
> delete38(id)

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
    api_instance = src.client.generated.DefectMatcherControllerApi(api_client)
    id = 56 # int | 

    try:
        await api_instance.delete38(id)
    except Exception as e:
        print("Exception when calling DefectMatcherControllerApi->delete38: %s\n" % e)
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
**204** | No Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch43**
> DefectMatcherDto patch43(id, defect_matcher_patch_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto
from src.client.generated.models.defect_matcher_patch_dto import DefectMatcherPatchDto
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
    api_instance = src.client.generated.DefectMatcherControllerApi(api_client)
    id = 56 # int | 
    defect_matcher_patch_dto = src.client.generated.DefectMatcherPatchDto() # DefectMatcherPatchDto | 

    try:
        api_response = await api_instance.patch43(id, defect_matcher_patch_dto)
        print("The response of DefectMatcherControllerApi->patch43:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefectMatcherControllerApi->patch43: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **defect_matcher_patch_dto** | [**DefectMatcherPatchDto**](DefectMatcherPatchDto.md)|  | 

### Return type

[**DefectMatcherDto**](DefectMatcherDto.md)

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

