# WorkflowSchemaCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **int** |  | 
**type** | [**TestCaseType**](TestCaseType.md) |  | 
**workflow_id** | **int** |  | 

## Example

```python
from src.client.generated.models.workflow_schema_create_dto import WorkflowSchemaCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowSchemaCreateDto from a JSON string
workflow_schema_create_dto_instance = WorkflowSchemaCreateDto.from_json(json)
# print the JSON string representation of the object
print(WorkflowSchemaCreateDto.to_json())

# convert the object into a dict
workflow_schema_create_dto_dict = workflow_schema_create_dto_instance.to_dict()
# create an instance of WorkflowSchemaCreateDto from a dict
workflow_schema_create_dto_from_dict = WorkflowSchemaCreateDto.from_dict(workflow_schema_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


