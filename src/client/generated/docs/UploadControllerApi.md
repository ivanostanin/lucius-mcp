# src.client.generated.UploadControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_job_run_by_uid**](UploadControllerApi.md#get_job_run_by_uid) | **GET** /api/upload/jobrun | Get information about job run by id
[**session_job_run**](UploadControllerApi.md#session_job_run) | **POST** /api/upload/session | Creates test session for manual upload
[**start**](UploadControllerApi.md#start) | **POST** /api/upload/run | Notifies about external job run start
[**start1**](UploadControllerApi.md#start1) | **POST** /api/upload/start | Notifies about external job run start
[**stop**](UploadControllerApi.md#stop) | **POST** /api/upload/stop | Notifies about external job run stop
[**upload_results**](UploadControllerApi.md#upload_results) | **POST** /api/upload | Upload test results
[**upload_results_archives**](UploadControllerApi.md#upload_results_archives) | **POST** /api/upload/archive | Upload archives with test results
[**upload_results_files**](UploadControllerApi.md#upload_results_files) | **POST** /api/upload/file | Upload files with test results


# **get_job_run_by_uid**
> ExternalRunResponseDto get_job_run_by_uid(project_id, job_uid, job_run_uid, job_run_id)

Get information about job run by id

### Example


```python
import src.client.generated
from src.client.generated.models.external_run_response_dto import ExternalRunResponseDto
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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    project_id = 56 # int | 
    job_uid = 'job_uid_example' # str | 
    job_run_uid = 'job_run_uid_example' # str | 
    job_run_id = 56 # int | 

    try:
        # Get information about job run by id
        api_response = await api_instance.get_job_run_by_uid(project_id, job_uid, job_run_uid, job_run_id)
        print("The response of UploadControllerApi->get_job_run_by_uid:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadControllerApi->get_job_run_by_uid: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | 
 **job_uid** | **str**|  | 
 **job_run_uid** | **str**|  | 
 **job_run_id** | **int**|  | 

### Return type

[**ExternalRunResponseDto**](ExternalRunResponseDto.md)

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

# **session_job_run**
> TestSessionResponseDto session_job_run(manual_session_request_dto)

Creates test session for manual upload

### Example


```python
import src.client.generated
from src.client.generated.models.manual_session_request_dto import ManualSessionRequestDto
from src.client.generated.models.test_session_response_dto import TestSessionResponseDto
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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    manual_session_request_dto = src.client.generated.ManualSessionRequestDto() # ManualSessionRequestDto | 

    try:
        # Creates test session for manual upload
        api_response = await api_instance.session_job_run(manual_session_request_dto)
        print("The response of UploadControllerApi->session_job_run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadControllerApi->session_job_run: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **manual_session_request_dto** | [**ManualSessionRequestDto**](ManualSessionRequestDto.md)|  | 

### Return type

[**TestSessionResponseDto**](TestSessionResponseDto.md)

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

# **start**
> ExternalRunResponseDto start(external_run_start_request_dto)

Notifies about external job run start

### Example


```python
import src.client.generated
from src.client.generated.models.external_run_response_dto import ExternalRunResponseDto
from src.client.generated.models.external_run_start_request_dto import ExternalRunStartRequestDto
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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    external_run_start_request_dto = src.client.generated.ExternalRunStartRequestDto() # ExternalRunStartRequestDto | 

    try:
        # Notifies about external job run start
        api_response = await api_instance.start(external_run_start_request_dto)
        print("The response of UploadControllerApi->start:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadControllerApi->start: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **external_run_start_request_dto** | [**ExternalRunStartRequestDto**](ExternalRunStartRequestDto.md)|  | 

### Return type

[**ExternalRunResponseDto**](ExternalRunResponseDto.md)

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

# **start1**
> ExternalRunResponseDto start1(external_run_start_request_dto)

Notifies about external job run start

### Example


```python
import src.client.generated
from src.client.generated.models.external_run_response_dto import ExternalRunResponseDto
from src.client.generated.models.external_run_start_request_dto import ExternalRunStartRequestDto
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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    external_run_start_request_dto = src.client.generated.ExternalRunStartRequestDto() # ExternalRunStartRequestDto | 

    try:
        # Notifies about external job run start
        api_response = await api_instance.start1(external_run_start_request_dto)
        print("The response of UploadControllerApi->start1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadControllerApi->start1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **external_run_start_request_dto** | [**ExternalRunStartRequestDto**](ExternalRunStartRequestDto.md)|  | 

### Return type

[**ExternalRunResponseDto**](ExternalRunResponseDto.md)

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

# **stop**
> ExternalRunResponseDto stop(external_run_stop_request_dto)

Notifies about external job run stop

### Example


```python
import src.client.generated
from src.client.generated.models.external_run_response_dto import ExternalRunResponseDto
from src.client.generated.models.external_run_stop_request_dto import ExternalRunStopRequestDto
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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    external_run_stop_request_dto = src.client.generated.ExternalRunStopRequestDto() # ExternalRunStopRequestDto | 

    try:
        # Notifies about external job run stop
        api_response = await api_instance.stop(external_run_stop_request_dto)
        print("The response of UploadControllerApi->stop:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadControllerApi->stop: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **external_run_stop_request_dto** | [**ExternalRunStopRequestDto**](ExternalRunStopRequestDto.md)|  | 

### Return type

[**ExternalRunResponseDto**](ExternalRunResponseDto.md)

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

# **upload_results**
> upload_results(id, archive=archive, file=file)

Upload test results

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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    id = 56 # int | 
    archive = None # List[bytes] |  (optional)
    file = None # List[bytes] |  (optional)

    try:
        # Upload test results
        await api_instance.upload_results(id, archive=archive, file=file)
    except Exception as e:
        print("Exception when calling UploadControllerApi->upload_results: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **archive** | **List[bytes]**|  | [optional] 
 **file** | **List[bytes]**|  | [optional] 

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

# **upload_results_archives**
> upload_results_archives(id, file)

Upload archives with test results

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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    id = 56 # int | 
    file = None # List[bytes] | 

    try:
        # Upload archives with test results
        await api_instance.upload_results_archives(id, file)
    except Exception as e:
        print("Exception when calling UploadControllerApi->upload_results_archives: %s\n" % e)
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

# **upload_results_files**
> upload_results_files(id, file)

Upload files with test results

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
    api_instance = src.client.generated.UploadControllerApi(api_client)
    id = 56 # int | 
    file = None # List[bytes] | 

    try:
        # Upload files with test results
        await api_instance.upload_results_files(id, file)
    except Exception as e:
        print("Exception when calling UploadControllerApi->upload_results_files: %s\n" % e)
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

