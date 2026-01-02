# CustomFieldValueWithTcCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field** | [**CustomFieldDto**](CustomFieldDto.md) |  | [optional] 
**var_global** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**test_cases_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_value_with_tc_count_dto import CustomFieldValueWithTcCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValueWithTcCountDto from a JSON string
custom_field_value_with_tc_count_dto_instance = CustomFieldValueWithTcCountDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValueWithTcCountDto.to_json())

# convert the object into a dict
custom_field_value_with_tc_count_dto_dict = custom_field_value_with_tc_count_dto_instance.to_dict()
# create an instance of CustomFieldValueWithTcCountDto from a dict
custom_field_value_with_tc_count_dto_from_dict = CustomFieldValueWithTcCountDto.from_dict(custom_field_value_with_tc_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


