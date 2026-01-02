# TestResultFlatDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignee** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 
**flaky** | **bool** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**layer_name** | **str** |  | [optional] 
**manual** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**tested_by** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_flat_dto import TestResultFlatDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultFlatDto from a JSON string
test_result_flat_dto_instance = TestResultFlatDto.from_json(json)
# print the JSON string representation of the object
print(TestResultFlatDto.to_json())

# convert the object into a dict
test_result_flat_dto_dict = test_result_flat_dto_instance.to_dict()
# create an instance of TestResultFlatDto from a dict
test_result_flat_dto_from_dict = TestResultFlatDto.from_dict(test_result_flat_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


