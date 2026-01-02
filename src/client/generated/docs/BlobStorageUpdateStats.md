# BlobStorageUpdateStats


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_case_attachment_count** | **int** |  | [optional] 
**test_fixture_result_attachment_count** | **int** |  | [optional] 
**test_fixture_result_count** | **int** |  | [optional] 
**test_result_attachment_count** | **int** |  | [optional] 
**test_result_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.blob_storage_update_stats import BlobStorageUpdateStats

# TODO update the JSON string below
json = "{}"
# create an instance of BlobStorageUpdateStats from a JSON string
blob_storage_update_stats_instance = BlobStorageUpdateStats.from_json(json)
# print the JSON string representation of the object
print(BlobStorageUpdateStats.to_json())

# convert the object into a dict
blob_storage_update_stats_dict = blob_storage_update_stats_instance.to_dict()
# create an instance of BlobStorageUpdateStats from a dict
blob_storage_update_stats_from_dict = BlobStorageUpdateStats.from_dict(blob_storage_update_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


