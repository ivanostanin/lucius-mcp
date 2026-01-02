# CustomFieldRawDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**archived** | **bool** |  | [optional] 
**default_custom_field_value_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**locked** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**required** | **bool** |  | [optional] 
**single_select** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_raw_dto import CustomFieldRawDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldRawDto from a JSON string
custom_field_raw_dto_instance = CustomFieldRawDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldRawDto.to_json())

# convert the object into a dict
custom_field_raw_dto_dict = custom_field_raw_dto_instance.to_dict()
# create an instance of CustomFieldRawDto from a dict
custom_field_raw_dto_from_dict = CustomFieldRawDto.from_dict(custom_field_raw_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


