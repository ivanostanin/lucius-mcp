# ProjectCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**abbr** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**favorite** | **bool** |  | [optional] 
**is_public** | **bool** |  | [optional] 
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.project_create_dto import ProjectCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectCreateDto from a JSON string
project_create_dto_instance = ProjectCreateDto.from_json(json)
# print the JSON string representation of the object
print(ProjectCreateDto.to_json())

# convert the object into a dict
project_create_dto_dict = project_create_dto_instance.to_dict()
# create an instance of ProjectCreateDto from a dict
project_create_dto_from_dict = ProjectCreateDto.from_dict(project_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


