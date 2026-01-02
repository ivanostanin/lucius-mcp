# TestResultRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignee** | **str** |  | [optional] 
**duration** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**test_case_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_row_dto import TestResultRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultRowDto from a JSON string
test_result_row_dto_instance = TestResultRowDto.from_json(json)
# print the JSON string representation of the object
print(TestResultRowDto.to_json())

# convert the object into a dict
test_result_row_dto_dict = test_result_row_dto_instance.to_dict()
# create an instance of TestResultRowDto from a dict
test_result_row_dto_from_dict = TestResultRowDto.from_dict(test_result_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


