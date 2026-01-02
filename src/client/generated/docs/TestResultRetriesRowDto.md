# TestResultRetriesRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**previous_retry** | [**Retry**](Retry.md) |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**total_retries** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_retries_row_dto import TestResultRetriesRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultRetriesRowDto from a JSON string
test_result_retries_row_dto_instance = TestResultRetriesRowDto.from_json(json)
# print the JSON string representation of the object
print(TestResultRetriesRowDto.to_json())

# convert the object into a dict
test_result_retries_row_dto_dict = test_result_retries_row_dto_instance.to_dict()
# create an instance of TestResultRetriesRowDto from a dict
test_result_retries_row_dto_from_dict = TestResultRetriesRowDto.from_dict(test_result_retries_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


