# AccessGroupBulkDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**ListSelectionDto**](ListSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.access_group_bulk_dto import AccessGroupBulkDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupBulkDto from a JSON string
access_group_bulk_dto_instance = AccessGroupBulkDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupBulkDto.to_json())

# convert the object into a dict
access_group_bulk_dto_dict = access_group_bulk_dto_instance.to_dict()
# create an instance of AccessGroupBulkDto from a dict
access_group_bulk_dto_from_dict = AccessGroupBulkDto.from_dict(access_group_bulk_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


