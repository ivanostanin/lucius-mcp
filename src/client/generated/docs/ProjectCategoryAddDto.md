# ProjectCategoryAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **int** |  | 

## Example

```python
from src.client.generated.models.project_category_add_dto import ProjectCategoryAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectCategoryAddDto from a JSON string
project_category_add_dto_instance = ProjectCategoryAddDto.from_json(json)
# print the JSON string representation of the object
print(ProjectCategoryAddDto.to_json())

# convert the object into a dict
project_category_add_dto_dict = project_category_add_dto_instance.to_dict()
# create an instance of ProjectCategoryAddDto from a dict
project_category_add_dto_from_dict = ProjectCategoryAddDto.from_dict(project_category_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


