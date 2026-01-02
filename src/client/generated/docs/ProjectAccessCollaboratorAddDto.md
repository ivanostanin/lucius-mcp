# ProjectAccessCollaboratorAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**collaborators** | [**List[ProjectCollaboratorAccessDto]**](ProjectCollaboratorAccessDto.md) |  | 

## Example

```python
from src.client.generated.models.project_access_collaborator_add_dto import ProjectAccessCollaboratorAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectAccessCollaboratorAddDto from a JSON string
project_access_collaborator_add_dto_instance = ProjectAccessCollaboratorAddDto.from_json(json)
# print the JSON string representation of the object
print(ProjectAccessCollaboratorAddDto.to_json())

# convert the object into a dict
project_access_collaborator_add_dto_dict = project_access_collaborator_add_dto_instance.to_dict()
# create an instance of ProjectAccessCollaboratorAddDto from a dict
project_access_collaborator_add_dto_from_dict = ProjectAccessCollaboratorAddDto.from_dict(project_access_collaborator_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


