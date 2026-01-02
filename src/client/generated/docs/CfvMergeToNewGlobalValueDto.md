# CfvMergeToNewGlobalValueDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | 
**default_value** | **bool** |  | 
**var_from** | **List[int]** |  | 
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.cfv_merge_to_new_global_value_dto import CfvMergeToNewGlobalValueDto

# TODO update the JSON string below
json = "{}"
# create an instance of CfvMergeToNewGlobalValueDto from a JSON string
cfv_merge_to_new_global_value_dto_instance = CfvMergeToNewGlobalValueDto.from_json(json)
# print the JSON string representation of the object
print(CfvMergeToNewGlobalValueDto.to_json())

# convert the object into a dict
cfv_merge_to_new_global_value_dto_dict = cfv_merge_to_new_global_value_dto_instance.to_dict()
# create an instance of CfvMergeToNewGlobalValueDto from a dict
cfv_merge_to_new_global_value_dto_from_dict = CfvMergeToNewGlobalValueDto.from_dict(cfv_merge_to_new_global_value_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


