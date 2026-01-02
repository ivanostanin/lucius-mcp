# MemberCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**role** | [**IdOnlyDto**](IdOnlyDto.md) |  | 

## Example

```python
from src.client.generated.models.member_create_dto import MemberCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of MemberCreateDto from a JSON string
member_create_dto_instance = MemberCreateDto.from_json(json)
# print the JSON string representation of the object
print(MemberCreateDto.to_json())

# convert the object into a dict
member_create_dto_dict = member_create_dto_instance.to_dict()
# create an instance of MemberCreateDto from a dict
member_create_dto_from_dict = MemberCreateDto.from_dict(member_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


