# ProjectSuggestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**abbr** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**is_public** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.project_suggest_dto import ProjectSuggestDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectSuggestDto from a JSON string
project_suggest_dto_instance = ProjectSuggestDto.from_json(json)
# print the JSON string representation of the object
print(ProjectSuggestDto.to_json())

# convert the object into a dict
project_suggest_dto_dict = project_suggest_dto_instance.to_dict()
# create an instance of ProjectSuggestDto from a dict
project_suggest_dto_from_dict = ProjectSuggestDto.from_dict(project_suggest_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


