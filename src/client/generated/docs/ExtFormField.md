# ExtFormField


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**depends_on_fields** | **List[str]** |  | [optional] 
**deprecated** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**required** | **bool** |  | [optional] 
**type** | **str** |  | 

## Example

```python
from src.client.generated.models.ext_form_field import ExtFormField

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormField from a JSON string
ext_form_field_instance = ExtFormField.from_json(json)
# print the JSON string representation of the object
print(ExtFormField.to_json())

# convert the object into a dict
ext_form_field_dict = ext_form_field_instance.to_dict()
# create an instance of ExtFormField from a dict
ext_form_field_from_dict = ExtFormField.from_dict(ext_form_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


