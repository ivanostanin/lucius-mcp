# src.client.generated.TestCaseTestPlanBulkControllerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_test_plan**](TestCaseTestPlanBulkControllerApi.md#create_test_plan) | **POST** /api/v2/test-case/bulk/test-plan/create | Create test plan from selected test cases


# **create_test_plan**
> TestPlanDto create_test_plan(test_case_test_plan_bulk_create_dto)

Create test plan from selected test cases

### Example


```python
import src.client.generated
from src.client.generated.models.test_case_test_plan_bulk_create_dto import TestCaseTestPlanBulkCreateDto
from src.client.generated.models.test_plan_dto import TestPlanDto
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
    api_instance = src.client.generated.TestCaseTestPlanBulkControllerApi(api_client)
    test_case_test_plan_bulk_create_dto = src.client.generated.TestCaseTestPlanBulkCreateDto() # TestCaseTestPlanBulkCreateDto | 

    try:
        # Create test plan from selected test cases
        api_response = await api_instance.create_test_plan(test_case_test_plan_bulk_create_dto)
        print("The response of TestCaseTestPlanBulkControllerApi->create_test_plan:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseTestPlanBulkControllerApi->create_test_plan: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_test_plan_bulk_create_dto** | [**TestCaseTestPlanBulkCreateDto**](TestCaseTestPlanBulkCreateDto.md)|  | 

### Return type

[**TestPlanDto**](TestPlanDto.md)

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

