# TestCaseRelationDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**target** | [**IdAndNameOnlyDto**](IdAndNameOnlyDto.md) |  | 
**type** | [**TestCaseRelationTypeDto**](TestCaseRelationTypeDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_relation_dto import TestCaseRelationDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseRelationDto from a JSON string
test_case_relation_dto_instance = TestCaseRelationDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseRelationDto.to_json())

# convert the object into a dict
test_case_relation_dto_dict = test_case_relation_dto_instance.to_dict()
# create an instance of TestCaseRelationDto from a dict
test_case_relation_dto_from_dict = TestCaseRelationDto.from_dict(test_case_relation_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


