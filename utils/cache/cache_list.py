# Cache Lists

# All Ocs Cache Lists
ocs_cache: list[dict[str, dict[str, str]]] = []
# Structure
# ocs_cache = {
#     {
#         "name": {
#              "rarity": str,
#             "character_info": str,
#             "image_link": str,}
#     },
#     ...

# For common rarity ocs
common_ocs_cache: list[dict[str, dict[str, str]]] = []
# Structure
# common_ocs_cache = {
#     {
#         "name": {
#             "character_info": str,
#             "image_link": str,}
#     },
#     ...

# For rare rarity ocs
rare_ocs_cache: list[dict[str, dict[str, str]]] = []
# Structure
# rare_ocs_cache = {
#     {
#         "name": {
#             "character_info": str,
#             "image_link": str,}
#     },
#     ...

# For epic rarity ocs
epic_ocs_cache: list[dict[str, dict[str, str]]] = []
# Structure
# epic_ocs_cache = {
#     {
#         "name": {
#             "character_info": str,
#             "image_link": str,}
#     },
#     ...

# For legendary rarity ocs
legendary_ocs_cache: list[dict[str, dict[str, str]]] = []
# Structure
# legendary_ocs_cache = {
#     {
#         "name": {
#             "character_info": str,
#             "image_link": str,}
#     },
#     ...

user_oc_inv_cache: dict[int, list[dict[str, str]]] = {}
# Structure
# user_oc_inv_cache = {
#     "user_id": [
#         {
#          "user_name": str,
#             "card_name": str,
#             "rarity": str,
#             "character_info": str,
#             "image_link": str,
#             "owned": int,
#         },
#         ...
#     ],
#     ...
