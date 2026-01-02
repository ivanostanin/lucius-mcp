# TestCaseSyncRqDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ignore_attachments** | **bool** |  | [optional] 
**ignore_cfv** | **bool** |  | [optional] 
**ignore_issue_links** | **bool** |  | [optional] 
**ignore_links** | **bool** |  | [optional] 
**ignore_members** | **bool** |  | [optional] 
**ignore_parameters** | **bool** |  | [optional] 
**ignore_scenario** | **bool** |  | [optional] 
**ignore_tags** | **bool** |  | [optional] 
**ignore_test_keys** | **bool** |  | [optional] 
**mapping** | [**List[TestCaseSyncFromTo]**](TestCaseSyncFromTo.md) |  | 
**name_suffix** | **str** |  | [optional] 
**status_id** | **int** |  | [optional] 
**workflow_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_sync_rq_dto import TestCaseSyncRqDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseSyncRqDto from a JSON string
test_case_sync_rq_dto_instance = TestCaseSyncRqDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseSyncRqDto.to_json())

# convert the object into a dict
test_case_sync_rq_dto_dict = test_case_sync_rq_dto_instance.to_dict()
# create an instance of TestCaseSyncRqDto from a dict
test_case_sync_rq_dto_from_dict = TestCaseSyncRqDto.from_dict(test_case_sync_rq_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


