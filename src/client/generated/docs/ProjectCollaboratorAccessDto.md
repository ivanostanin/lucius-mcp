# ProjectCollaboratorAccessDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**permission_set_id** | **int** |  | 
**permission_set_name** | **str** |  | [optional] 
**project_groups** | [**List[ProjectGroupAccessDto]**](ProjectGroupAccessDto.md) |  | [optional] 
**username** | **str** |  | 

## Example

```python
from src.client.generated.models.project_collaborator_access_dto import ProjectCollaboratorAccessDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectCollaboratorAccessDto from a JSON string
project_collaborator_access_dto_instance = ProjectCollaboratorAccessDto.from_json(json)
# print the JSON string representation of the object
print(ProjectCollaboratorAccessDto.to_json())

# convert the object into a dict
project_collaborator_access_dto_dict = project_collaborator_access_dto_instance.to_dict()
# create an instance of ProjectCollaboratorAccessDto from a dict
project_collaborator_access_dto_from_dict = ProjectCollaboratorAccessDto.from_dict(project_collaborator_access_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


