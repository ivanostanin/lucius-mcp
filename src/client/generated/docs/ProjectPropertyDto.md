# ProjectPropertyDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.project_property_dto import ProjectPropertyDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPropertyDto from a JSON string
project_property_dto_instance = ProjectPropertyDto.from_json(json)
# print the JSON string representation of the object
print(ProjectPropertyDto.to_json())

# convert the object into a dict
project_property_dto_dict = project_property_dto_instance.to_dict()
# create an instance of ProjectPropertyDto from a dict
project_property_dto_from_dict = ProjectPropertyDto.from_dict(project_property_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


