# CustomFieldValueWithCfDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field** | [**CustomFieldDto**](CustomFieldDto.md) |  | [optional] 
**var_global** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValueWithCfDto from a JSON string
custom_field_value_with_cf_dto_instance = CustomFieldValueWithCfDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValueWithCfDto.to_json())

# convert the object into a dict
custom_field_value_with_cf_dto_dict = custom_field_value_with_cf_dto_instance.to_dict()
# create an instance of CustomFieldValueWithCfDto from a dict
custom_field_value_with_cf_dto_from_dict = CustomFieldValueWithCfDto.from_dict(custom_field_value_with_cf_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


