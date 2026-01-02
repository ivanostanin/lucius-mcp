# WorkflowSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 
**type** | [**TestCaseType**](TestCaseType.md) |  | [optional] 
**workflow** | [**WorkflowDto**](WorkflowDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.workflow_schema_dto import WorkflowSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowSchemaDto from a JSON string
workflow_schema_dto_instance = WorkflowSchemaDto.from_json(json)
# print the JSON string representation of the object
print(WorkflowSchemaDto.to_json())

# convert the object into a dict
workflow_schema_dto_dict = workflow_schema_dto_instance.to_dict()
# create an instance of WorkflowSchemaDto from a dict
workflow_schema_dto_from_dict = WorkflowSchemaDto.from_dict(workflow_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


