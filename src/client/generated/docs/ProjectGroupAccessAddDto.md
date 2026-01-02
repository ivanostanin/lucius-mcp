# ProjectGroupAccessAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**group_id** | **int** |  | 
**permission_set_id** | **int** |  | 

## Example

```python
from src.client.generated.models.project_group_access_add_dto import ProjectGroupAccessAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectGroupAccessAddDto from a JSON string
project_group_access_add_dto_instance = ProjectGroupAccessAddDto.from_json(json)
# print the JSON string representation of the object
print(ProjectGroupAccessAddDto.to_json())

# convert the object into a dict
project_group_access_add_dto_dict = project_group_access_add_dto_instance.to_dict()
# create an instance of ProjectGroupAccessAddDto from a dict
project_group_access_add_dto_from_dict = ProjectGroupAccessAddDto.from_dict(project_group_access_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


