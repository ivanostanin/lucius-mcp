# ProjectGroupAccessDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**group** | [**AccessGroupDto**](AccessGroupDto.md) |  | 
**permission_set_id** | **int** |  | 
**permission_set_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.project_group_access_dto import ProjectGroupAccessDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectGroupAccessDto from a JSON string
project_group_access_dto_instance = ProjectGroupAccessDto.from_json(json)
# print the JSON string representation of the object
print(ProjectGroupAccessDto.to_json())

# convert the object into a dict
project_group_access_dto_dict = project_group_access_dto_instance.to_dict()
# create an instance of ProjectGroupAccessDto from a dict
project_group_access_dto_from_dict = ProjectGroupAccessDto.from_dict(project_group_access_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


