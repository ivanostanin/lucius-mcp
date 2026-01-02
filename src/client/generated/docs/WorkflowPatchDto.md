# WorkflowPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**statuses** | [**List[IdOnlyDto]**](IdOnlyDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.workflow_patch_dto import WorkflowPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowPatchDto from a JSON string
workflow_patch_dto_instance = WorkflowPatchDto.from_json(json)
# print the JSON string representation of the object
print(WorkflowPatchDto.to_json())

# convert the object into a dict
workflow_patch_dto_dict = workflow_patch_dto_instance.to_dict()
# create an instance of WorkflowPatchDto from a dict
workflow_patch_dto_from_dict = WorkflowPatchDto.from_dict(workflow_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


