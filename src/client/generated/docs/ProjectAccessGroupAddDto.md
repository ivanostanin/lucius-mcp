# ProjectAccessGroupAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**groups** | [**List[ProjectGroupAccessAddDto]**](ProjectGroupAccessAddDto.md) |  | 

## Example

```python
from src.client.generated.models.project_access_group_add_dto import ProjectAccessGroupAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectAccessGroupAddDto from a JSON string
project_access_group_add_dto_instance = ProjectAccessGroupAddDto.from_json(json)
# print the JSON string representation of the object
print(ProjectAccessGroupAddDto.to_json())

# convert the object into a dict
project_access_group_add_dto_dict = project_access_group_add_dto_instance.to_dict()
# create an instance of ProjectAccessGroupAddDto from a dict
project_access_group_add_dto_from_dict = ProjectAccessGroupAddDto.from_dict(project_access_group_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


