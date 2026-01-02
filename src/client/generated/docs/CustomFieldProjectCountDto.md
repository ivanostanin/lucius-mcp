# CustomFieldProjectCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**projects_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_project_count_dto import CustomFieldProjectCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldProjectCountDto from a JSON string
custom_field_project_count_dto_instance = CustomFieldProjectCountDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldProjectCountDto.to_json())

# convert the object into a dict
custom_field_project_count_dto_dict = custom_field_project_count_dto_instance.to_dict()
# create an instance of CustomFieldProjectCountDto from a dict
custom_field_project_count_dto_from_dict = CustomFieldProjectCountDto.from_dict(custom_field_project_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


