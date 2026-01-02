# TestCaseCreateV2Dto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **bool** |  | [optional] 
**custom_fields** | [**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md) |  | [optional] 
**deleted** | **bool** |  | [optional] 
**description** | **str** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**external** | **bool** |  | [optional] 
**full_name** | **str** |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**members** | [**List[MemberDto]**](MemberDto.md) |  | [optional] 
**name** | **str** |  | 
**precondition** | **str** |  | [optional] 
**project_id** | **int** |  | 
**scenario** | [**TestCaseScenarioV2Dto**](TestCaseScenarioV2Dto.md) |  | [optional] 
**status_id** | **int** |  | [optional] 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | [optional] 
**test_layer_id** | **int** |  | [optional] 
**workflow_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseCreateV2Dto from a JSON string
test_case_create_v2_dto_instance = TestCaseCreateV2Dto.from_json(json)
# print the JSON string representation of the object
print(TestCaseCreateV2Dto.to_json())

# convert the object into a dict
test_case_create_v2_dto_dict = test_case_create_v2_dto_instance.to_dict()
# create an instance of TestCaseCreateV2Dto from a dict
test_case_create_v2_dto_from_dict = TestCaseCreateV2Dto.from_dict(test_case_create_v2_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


