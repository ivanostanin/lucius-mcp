# CustomFieldMergeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_from** | **int** |  | [optional] 
**to** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_merge_dto import CustomFieldMergeDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldMergeDto from a JSON string
custom_field_merge_dto_instance = CustomFieldMergeDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldMergeDto.to_json())

# convert the object into a dict
custom_field_merge_dto_dict = custom_field_merge_dto_instance.to_dict()
# create an instance of CustomFieldMergeDto from a dict
custom_field_merge_dto_from_dict = CustomFieldMergeDto.from_dict(custom_field_merge_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


