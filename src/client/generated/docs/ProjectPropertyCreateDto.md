# ProjectPropertyCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**project_id** | **int** |  | 
**value** | **str** |  | 

## Example

```python
from src.client.generated.models.project_property_create_dto import ProjectPropertyCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPropertyCreateDto from a JSON string
project_property_create_dto_instance = ProjectPropertyCreateDto.from_json(json)
# print the JSON string representation of the object
print(ProjectPropertyCreateDto.to_json())

# convert the object into a dict
project_property_create_dto_dict = project_property_create_dto_instance.to_dict()
# create an instance of ProjectPropertyCreateDto from a dict
project_property_create_dto_from_dict = ProjectPropertyCreateDto.from_dict(project_property_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


