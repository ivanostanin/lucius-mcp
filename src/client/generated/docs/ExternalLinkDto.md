# ExternalLinkDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.external_link_dto import ExternalLinkDto

# TODO update the JSON string below
json = "{}"
# create an instance of ExternalLinkDto from a JSON string
external_link_dto_instance = ExternalLinkDto.from_json(json)
# print the JSON string representation of the object
print(ExternalLinkDto.to_json())

# convert the object into a dict
external_link_dto_dict = external_link_dto_instance.to_dict()
# create an instance of ExternalLinkDto from a dict
external_link_dto_from_dict = ExternalLinkDto.from_dict(external_link_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


