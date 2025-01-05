url = "https://sellingpartnerapi-eu.amazon.com/reports/2021-06-30/documents/amzn1.spdoc.1.4.eu.9c087a4a-d777-4467-ac27-8f43b2b50b21.TJI05HVRJYWXF.2650"
url = "https://tortuga-prod-eu.s3-eu-west-1.amazonaws.com/ad6d27e8-8f51-4dba-a854-d6a33b78a696.amzn1.tortuga.4.eu.T1USAQB9HJEN9P?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241228T113337Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=AKIAX2ZVOZFBF6SMBQZN%2F20241228%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=0a62d5205a6a596decba004465ad5e23e7641451bd2e02f6b77c25137e984725"


import requests

# response = requests.get(url)
# print(response.content)
# print("--------------")
# print("-------------")

# print(response.headers)
# print("--------------")
# decoded_content = response.text
# # print(response.json())
# print(decoded_content)
# import csv
# import json
# reader = csv.DictReader(decoded_content.splitlines(), delimiter='\t')
import gzip
import json
res = requests.get("https://tortuga-prod-eu.s3-eu-west-1.amazonaws.com/818580e7-9bfd-42fc-a67f-05d05d3308ac.amzn1.tortuga.4.eu.T1EZ7DFPZ9OOOA?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241228T173458Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=AKIAX2ZVOZFBF6SMBQZN%2F20241228%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=9f903c446ddfdf8c68403cf6d2958edd69aa52da8ab857005a2dd542f37364e3")
compressed_data = res.content
decompressed_data = gzip.decompress(compressed_data)
json_data = decompressed_data.decode('utf-8')
print(json_data)
# parsed_data = json.load(json_data)
# print(json.dumps(parsed_data, indent=4))
with open("data_analytic_new.json", "w") as f:
    f.write(json_data)




# data_list =[]
# for row in reader:
#     data = {
#         "asin": row["asin"],
#         "sku": row["sku"],
#         "product_name": row["product-name"],
#         "per-unit-volume": row["per-unit-volume"],
#         "afn-inbound-working-quantity": row["afn-inbound-working-quantity"],
#         "condition": row["condition"],
#         "your-price": row["your-price"],
#         "mfn-listing-exists": row["mfn-listing-exists"],
#         "mfn-fulfillable-quantity": row["mfn-fulfillable-quantity"],
#         "afn-listing-exists": row["afn-listing-exists"],
#         "afn-warehouse-quantity": row["afn-warehouse-quantity"],
#         "afn-fulfillable-quantity": row["afn-fulfillable-quantity"],
#         "afn-unsellable-quantity": row["afn-unsellable-quantity"],
#         "afn-reserved-quantity": row["afn-reserved-quantity"],
#         "afn-total-quantity": row["afn-total-quantity"],
#         "afn-inbound-shipped-quantity": row["afn-inbound-shipped-quantity"],
#         "afn-inbound-receiving-quantity": row["afn-inbound-receiving-quantity"],
#         "afn-researching-quantity": row["afn-researching-quantity"],
#         "afn-reserved-future-supply": row["afn-reserved-future-supply"],
#         "afn-future-supply-buyable": row["afn-future-supply-buyable"],
#         "store": row["store"],
#     }
#     data_list.append(data)

# print(data_list)

# with open("data_new.json", "w") as f:
#     f.write(json.dumps(data_list))
