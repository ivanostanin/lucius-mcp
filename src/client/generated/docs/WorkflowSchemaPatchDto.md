# WorkflowSchemaPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | [**TestCaseType**](TestCaseType.md) |  | [optional] 
**workflow_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.workflow_schema_patch_dto import WorkflowSchemaPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowSchemaPatchDto from a JSON string
workflow_schema_patch_dto_instance = WorkflowSchemaPatchDto.from_json(json)
# print the JSON string representation of the object
print(WorkflowSchemaPatchDto.to_json())

# convert the object into a dict
workflow_schema_patch_dto_dict = workflow_schema_patch_dto_instance.to_dict()
# create an instance of WorkflowSchemaPatchDto from a dict
workflow_schema_patch_dto_from_dict = WorkflowSchemaPatchDto.from_dict(workflow_schema_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


