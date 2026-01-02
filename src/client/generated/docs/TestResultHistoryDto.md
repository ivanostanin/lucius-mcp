# TestResultHistoryDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 
**environment** | [**List[EnvVarValueDto]**](EnvVarValueDto.md) |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**launch** | [**IdAndNameOnlyDto**](IdAndNameOnlyDto.md) |  | [optional] 
**message** | **str** |  | [optional] 
**parameters** | [**List[TestResultParameterDto]**](TestResultParameterDto.md) |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**tested_by** | **str** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_history_dto import TestResultHistoryDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultHistoryDto from a JSON string
test_result_history_dto_instance = TestResultHistoryDto.from_json(json)
# print the JSON string representation of the object
print(TestResultHistoryDto.to_json())

# convert the object into a dict
test_result_history_dto_dict = test_result_history_dto_instance.to_dict()
# create an instance of TestResultHistoryDto from a dict
test_result_history_dto_from_dict = TestResultHistoryDto.from_dict(test_result_history_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


