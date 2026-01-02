# ExtFormFieldNumber


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_value** | **int** |  | [optional] 
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_number import ExtFormFieldNumber

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldNumber from a JSON string
ext_form_field_number_instance = ExtFormFieldNumber.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldNumber.to_json())

# convert the object into a dict
ext_form_field_number_dict = ext_form_field_number_instance.to_dict()
# create an instance of ExtFormFieldNumber from a dict
ext_form_field_number_from_dict = ExtFormFieldNumber.from_dict(ext_form_field_number_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


