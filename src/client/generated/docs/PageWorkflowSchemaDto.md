# PageWorkflowSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[WorkflowSchemaDto]**](WorkflowSchemaDto.md) |  | [optional] 
**empty** | **bool** |  | [optional] 
**first** | **bool** |  | [optional] 
**last** | **bool** |  | [optional] 
**number** | **int** |  | [optional] 
**number_of_elements** | **int** |  | [optional] 
**pageable** | [**Pageable**](Pageable.md) |  | [optional] 
**size** | **int** |  | [optional] 
**sort** | [**PageAccessGroupDtoSort**](PageAccessGroupDtoSort.md) |  | [optional] 
**total_elements** | **int** |  | [optional] 
**total_pages** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.page_workflow_schema_dto import PageWorkflowSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of PageWorkflowSchemaDto from a JSON string
page_workflow_schema_dto_instance = PageWorkflowSchemaDto.from_json(json)
# print the JSON string representation of the object
print(PageWorkflowSchemaDto.to_json())

# convert the object into a dict
page_workflow_schema_dto_dict = page_workflow_schema_dto_instance.to_dict()
# create an instance of PageWorkflowSchemaDto from a dict
page_workflow_schema_dto_from_dict = PageWorkflowSchemaDto.from_dict(page_workflow_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


