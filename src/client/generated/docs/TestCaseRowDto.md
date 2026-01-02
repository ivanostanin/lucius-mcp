# TestCaseRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**StatusDto**](StatusDto.md) |  | [optional] 
**test_layer** | [**TestLayerDto**](TestLayerDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_row_dto import TestCaseRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseRowDto from a JSON string
test_case_row_dto_instance = TestCaseRowDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseRowDto.to_json())

# convert the object into a dict
test_case_row_dto_dict = test_case_row_dto_instance.to_dict()
# create an instance of TestCaseRowDto from a dict
test_case_row_dto_from_dict = TestCaseRowDto.from_dict(test_case_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


