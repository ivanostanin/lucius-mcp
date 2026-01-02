# ProjectCollaboratorDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**username** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.project_collaborator_dto import ProjectCollaboratorDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectCollaboratorDto from a JSON string
project_collaborator_dto_instance = ProjectCollaboratorDto.from_json(json)
# print the JSON string representation of the object
print(ProjectCollaboratorDto.to_json())

# convert the object into a dict
project_collaborator_dto_dict = project_collaborator_dto_instance.to_dict()
# create an instance of ProjectCollaboratorDto from a dict
project_collaborator_dto_from_dict = ProjectCollaboratorDto.from_dict(project_collaborator_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


