# TestResultCreateV2Dto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | [**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md) |  | [optional] 
**description** | **str** |  | [optional] 
**duration** | **int** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**external** | **bool** |  | [optional] 
**full_name** | **str** |  | [optional] 
**launch_id** | **int** |  | 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**manual** | **bool** |  | [optional] 
**members** | [**List[MemberDto]**](MemberDto.md) |  | [optional] 
**message** | **str** |  | [optional] 
**name** | **str** |  | 
**precondition** | **str** |  | [optional] 
**scenario** | [**TestResultScenarioV2Dto**](TestResultScenarioV2Dto.md) |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | 
**stop** | **int** |  | [optional] 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**test_layer_id** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_create_v2_dto import TestResultCreateV2Dto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultCreateV2Dto from a JSON string
test_result_create_v2_dto_instance = TestResultCreateV2Dto.from_json(json)
# print the JSON string representation of the object
print(TestResultCreateV2Dto.to_json())

# convert the object into a dict
test_result_create_v2_dto_dict = test_result_create_v2_dto_instance.to_dict()
# create an instance of TestResultCreateV2Dto from a dict
test_result_create_v2_dto_from_dict = TestResultCreateV2Dto.from_dict(test_result_create_v2_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


