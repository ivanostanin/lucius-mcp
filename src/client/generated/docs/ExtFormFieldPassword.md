# ExtFormFieldPassword


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_password import ExtFormFieldPassword

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldPassword from a JSON string
ext_form_field_password_instance = ExtFormFieldPassword.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldPassword.to_json())

# convert the object into a dict
ext_form_field_password_dict = ext_form_field_password_instance.to_dict()
# create an instance of ExtFormFieldPassword from a dict
ext_form_field_password_from_dict = ExtFormFieldPassword.from_dict(ext_form_field_password_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


