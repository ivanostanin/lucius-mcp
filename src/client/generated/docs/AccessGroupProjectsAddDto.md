# AccessGroupProjectsAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**projects** | [**List[AccessGroupProjectAccessDto]**](AccessGroupProjectAccessDto.md) |  | 

## Example

```python
from src.client.generated.models.access_group_projects_add_dto import AccessGroupProjectsAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupProjectsAddDto from a JSON string
access_group_projects_add_dto_instance = AccessGroupProjectsAddDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupProjectsAddDto.to_json())

# convert the object into a dict
access_group_projects_add_dto_dict = access_group_projects_add_dto_instance.to_dict()
# create an instance of AccessGroupProjectsAddDto from a dict
access_group_projects_add_dto_from_dict = AccessGroupProjectsAddDto.from_dict(access_group_projects_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


