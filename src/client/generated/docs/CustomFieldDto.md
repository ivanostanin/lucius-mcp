# CustomFieldDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**archived** | **bool** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**default_custom_field_value_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**locked** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**required** | **bool** |  | [optional] 
**single_select** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_dto import CustomFieldDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldDto from a JSON string
custom_field_dto_instance = CustomFieldDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldDto.to_json())

# convert the object into a dict
custom_field_dto_dict = custom_field_dto_instance.to_dict()
# create an instance of CustomFieldDto from a dict
custom_field_dto_from_dict = CustomFieldDto.from_dict(custom_field_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


