# src.client.generated.UploadTestResultControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_content**](UploadTestResultControllerApi.md#add_content) | **POST** /api/upload/test-result/{id}/attachment | 
[**add_fixture_content**](UploadTestResultControllerApi.md#add_fixture_content) | **POST** /api/upload/test-fixture-result/{id}/attachment | 
[**upload_test_fixture_results**](UploadTestResultControllerApi.md#upload_test_fixture_results) | **POST** /api/upload/test-result/{id}/test-fixture-result | 
[**upload_test_results**](UploadTestResultControllerApi.md#upload_test_results) | **POST** /api/upload/test-result | Manual upload test-result data


# **add_content**
> add_content(id, file)

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
    api_instance = src.client.generated.UploadTestResultControllerApi(api_client)
    id = 56 # int | 
    file = None # List[bytes] | 

    try:
        await api_instance.add_content(id, file)
    except Exception as e:
        print("Exception when calling UploadTestResultControllerApi->add_content: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **file** | **List[bytes]**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_fixture_content**
> add_fixture_content(id, file)

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
    api_instance = src.client.generated.UploadTestResultControllerApi(api_client)
    id = 56 # int | 
    file = None # List[bytes] | 

    try:
        await api_instance.add_fixture_content(id, file)
    except Exception as e:
        print("Exception when calling UploadTestResultControllerApi->add_fixture_content: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **file** | **List[bytes]**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_test_fixture_results**
> UploadResultsResponseDto upload_test_fixture_results(id, upload_fixtures_results_dto)

### Example


```python
import src.client.generated
from src.client.generated.models.upload_fixtures_results_dto import UploadFixturesResultsDto
from src.client.generated.models.upload_results_response_dto import UploadResultsResponseDto
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
    api_instance = src.client.generated.UploadTestResultControllerApi(api_client)
    id = 56 # int | 
    upload_fixtures_results_dto = src.client.generated.UploadFixturesResultsDto() # UploadFixturesResultsDto | 

    try:
        api_response = await api_instance.upload_test_fixture_results(id, upload_fixtures_results_dto)
        print("The response of UploadTestResultControllerApi->upload_test_fixture_results:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadTestResultControllerApi->upload_test_fixture_results: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **upload_fixtures_results_dto** | [**UploadFixturesResultsDto**](UploadFixturesResultsDto.md)|  | 

### Return type

[**UploadResultsResponseDto**](UploadResultsResponseDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Accepted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_test_results**
> UploadResultsResponseDto upload_test_results(upload_results_dto)

Manual upload test-result data

### Example


```python
import src.client.generated
from src.client.generated.models.upload_results_dto import UploadResultsDto
from src.client.generated.models.upload_results_response_dto import UploadResultsResponseDto
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
    api_instance = src.client.generated.UploadTestResultControllerApi(api_client)
    upload_results_dto = src.client.generated.UploadResultsDto() # UploadResultsDto | 

    try:
        # Manual upload test-result data
        api_response = await api_instance.upload_test_results(upload_results_dto)
        print("The response of UploadTestResultControllerApi->upload_test_results:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadTestResultControllerApi->upload_test_results: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upload_results_dto** | [**UploadResultsDto**](UploadResultsDto.md)|  | 

### Return type

[**UploadResultsResponseDto**](UploadResultsResponseDto.md)

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

