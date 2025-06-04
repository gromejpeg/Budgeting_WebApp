# import requests
#
# # ACCESS_TOKEN = "g8_VguDBKmT2zSukz82OPJmUp9izDnnLulpAr35Nnhk"
# ACCESS_TOKEN = st.secrets["YNAB_ACCESS_TOKEN"]
#
# headers = {
#     "Authorization": f"Bearer {ACCESS_TOKEN}"
# }
#
# response = requests.get("https://api.ynab.com/v1/budgets", headers=headers)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json())
