# WorkflowRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.workflow_row_dto import WorkflowRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowRowDto from a JSON string
workflow_row_dto_instance = WorkflowRowDto.from_json(json)
# print the JSON string representation of the object
print(WorkflowRowDto.to_json())

# convert the object into a dict
workflow_row_dto_dict = workflow_row_dto_instance.to_dict()
# create an instance of WorkflowRowDto from a dict
workflow_row_dto_from_dict = WorkflowRowDto.from_dict(workflow_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


