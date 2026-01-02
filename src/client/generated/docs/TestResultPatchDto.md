# TestResultPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | [**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md) |  | [optional] 
**description** | **str** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**full_name** | **str** |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**members** | [**List[MemberDto]**](MemberDto.md) |  | [optional] 
**name** | **str** |  | 
**precondition** | **str** |  | [optional] 
**scenario** | [**TestResultScenarioDto**](TestResultScenarioDto.md) |  | [optional] 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | [optional] 
**test_layer_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_patch_dto import TestResultPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultPatchDto from a JSON string
test_result_patch_dto_instance = TestResultPatchDto.from_json(json)
# print the JSON string representation of the object
print(TestResultPatchDto.to_json())

# convert the object into a dict
test_result_patch_dto_dict = test_result_patch_dto_instance.to_dict()
# create an instance of TestResultPatchDto from a dict
test_result_patch_dto_from_dict = TestResultPatchDto.from_dict(test_result_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


