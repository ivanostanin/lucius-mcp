# TestCaseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **bool** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**deleted** | **bool** |  | [optional] 
**description** | **str** |  | [optional] 
**description_html** | **str** |  | [optional] 
**editable** | **bool** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**expected_result_html** | **str** |  | [optional] 
**external** | **bool** |  | [optional] 
**full_name** | **str** |  | [optional] 
**hash** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**precondition** | **str** |  | [optional] 
**precondition_html** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**status** | [**StatusDto**](StatusDto.md) |  | [optional] 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | [optional] 
**test_layer** | [**TestLayerDto**](TestLayerDto.md) |  | [optional] 
**workflow** | [**WorkflowRowDto**](WorkflowRowDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_dto import TestCaseDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseDto from a JSON string
test_case_dto_instance = TestCaseDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseDto.to_json())

# convert the object into a dict
test_case_dto_dict = test_case_dto_instance.to_dict()
# create an instance of TestCaseDto from a dict
test_case_dto_from_dict = TestCaseDto.from_dict(test_case_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


