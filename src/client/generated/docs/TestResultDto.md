# TestResultDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignee** | **str** |  | [optional] 
**category** | [**CategoryDto**](CategoryDto.md) |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**description** | **str** |  | [optional] 
**description_html** | **str** |  | [optional] 
**duration** | **int** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**expected_result_html** | **str** |  | [optional] 
**external** | **bool** |  | [optional] 
**flaky** | **bool** |  | [optional] 
**full_name** | **str** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**history_key** | **str** |  | [optional] 
**host_id** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**job_run** | [**JobRunDto**](JobRunDto.md) |  | [optional] 
**known** | **bool** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**launch_id** | **int** |  | [optional] 
**layer** | [**TestLayerDto**](TestLayerDto.md) |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**manual** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**muted** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**parameters** | [**List[TestResultParameterDto]**](TestResultParameterDto.md) |  | [optional] 
**precondition** | **str** |  | [optional] 
**precondition_html** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**retried_by** | [**IdAndNameOnlyDto**](IdAndNameOnlyDto.md) |  | [optional] 
**scenario_key** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**tested_by** | **str** |  | [optional] 
**thread_id** | **str** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_dto import TestResultDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultDto from a JSON string
test_result_dto_instance = TestResultDto.from_json(json)
# print the JSON string representation of the object
print(TestResultDto.to_json())

# convert the object into a dict
test_result_dto_dict = test_result_dto_instance.to_dict()
# create an instance of TestResultDto from a dict
test_result_dto_from_dict = TestResultDto.from_dict(test_result_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


