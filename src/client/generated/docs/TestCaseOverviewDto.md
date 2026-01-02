# TestCaseOverviewDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **bool** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**custom_fields** | [**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md) |  | [optional] 
**deleted** | **bool** |  | [optional] 
**description** | **str** |  | [optional] 
**description_html** | **str** |  | [optional] 
**editable** | **bool** |  | [optional] 
**examples** | [**List[TestCaseExampleDto]**](TestCaseExampleDto.md) |  | [optional] 
**expected_result** | **str** |  | [optional] 
**expected_result_html** | **str** |  | [optional] 
**external** | **bool** |  | [optional] 
**full_name** | **str** |  | [optional] 
**has_manual_scenario** | **bool** |  | [optional] 
**hash** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**layer** | [**TestLayerDto**](TestLayerDto.md) |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**members** | [**List[MemberDto]**](MemberDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**parameters** | [**List[TestCaseParameterDto]**](TestCaseParameterDto.md) |  | [optional] 
**precondition** | **str** |  | [optional] 
**precondition_html** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**scenario** | [**TestCaseScenarioDto**](TestCaseScenarioDto.md) |  | [optional] 
**status** | [**StatusDto**](StatusDto.md) |  | [optional] 
**style** | [**TestCaseStyle**](TestCaseStyle.md) |  | [optional] 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | [optional] 
**test_keys** | [**List[TestKeyDto]**](TestKeyDto.md) |  | [optional] 
**workflow** | [**WorkflowDto**](WorkflowDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_overview_dto import TestCaseOverviewDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseOverviewDto from a JSON string
test_case_overview_dto_instance = TestCaseOverviewDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseOverviewDto.to_json())

# convert the object into a dict
test_case_overview_dto_dict = test_case_overview_dto_instance.to_dict()
# create an instance of TestCaseOverviewDto from a dict
test_case_overview_dto_from_dict = TestCaseOverviewDto.from_dict(test_case_overview_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


