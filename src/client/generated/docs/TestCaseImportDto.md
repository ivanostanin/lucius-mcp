# TestCaseImportDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | [**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md) |  | [optional] 
**description** | **str** |  | [optional] 
**description_html** | **str** |  | [optional] 
**examples** | [**List[TestCaseExampleDto]**](TestCaseExampleDto.md) |  | [optional] 
**expected_result** | **str** |  | [optional] 
**expected_result_html** | **str** |  | [optional] 
**full_name** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**layer** | [**TestLayerDto**](TestLayerDto.md) |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**members** | [**List[MemberDto]**](MemberDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**parameters** | [**List[TestCaseParameterDto]**](TestCaseParameterDto.md) |  | [optional] 
**precondition** | **str** |  | [optional] 
**precondition_html** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**scenario** | [**TestCaseScenarioV2Dto**](TestCaseScenarioV2Dto.md) |  | [optional] 
**status** | [**StatusDto**](StatusDto.md) |  | [optional] 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | [optional] 
**test_keys** | [**List[TestKeyDto]**](TestKeyDto.md) |  | [optional] 
**workflow** | [**WorkflowDto**](WorkflowDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_import_dto import TestCaseImportDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseImportDto from a JSON string
test_case_import_dto_instance = TestCaseImportDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseImportDto.to_json())

# convert the object into a dict
test_case_import_dto_dict = test_case_import_dto_instance.to_dict()
# create an instance of TestCaseImportDto from a dict
test_case_import_dto_from_dict = TestCaseImportDto.from_dict(test_case_import_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


