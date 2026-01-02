# NameOnlyDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.name_only_dto import NameOnlyDto

# TODO update the JSON string below
json = "{}"
# create an instance of NameOnlyDto from a JSON string
name_only_dto_instance = NameOnlyDto.from_json(json)
# print the JSON string representation of the object
print(NameOnlyDto.to_json())

# convert the object into a dict
name_only_dto_dict = name_only_dto_instance.to_dict()
# create an instance of NameOnlyDto from a dict
name_only_dto_from_dict = NameOnlyDto.from_dict(name_only_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


