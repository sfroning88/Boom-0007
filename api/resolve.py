def resolve_objects(extracted=None, object_mode=None):
    if extracted is None or object_mode is None:
        print("ERROR: No object or mode was passed into resolve function")
        return None

    if object_mode not in ["Customer", "Vendor"]:
        print("ERROR: Incorrect enum mode passed into resolve function")
        return None

    import concurrent.futures
    from tqdm import tqdm

    from api.retrieve import get_database
    pre_object = get_database(query_mode=object_mode)

    if pre_object is None or object_mode not in list(pre_object.keys()):
        print(f"WARNING: Please upload {object_mode}s to QBO before posting invoices")
        return None

    post_object = pre_object[object_mode]

    # pull all existing objects
    objects_existing = []
    for single in post_object:
        objects_existing.append(single['DisplayName'])
    if len(objects_existing) == 0:
        return extracted

    print(f"CHECKPOINT: Found {len(objects_existing)} existing {object_mode}")

    objects_new = []
    for single in list(extracted.values()):
        objects_new.append(single['Name'])
    objects_new = list(set(objects_new))
    objects_new.sort()

    # remove any duplicate customers
    for new_name in objects_new:
        if new_name in objects_existing:
            objects_new.remove(new_name)

    objects_added = []
    for new_name in objects_new:

        if object_mode == "Customer":
            # Create dummy customer object and add to database
            dummy_customer = {
                "Customer": new_name,
                "Primary Contact": "",
                "Main Phone": "",
                "Bill To": "",
                "Balance Total": 0.0
            }
            objects_added.append(dummy_customer)

        elif object_mode == "Vendor":
            dummy_vendor = {
                "Vendor": new_name,
                "Account #": "",
                "Primary Contact": "",
                "Main Phone": "",
                "Bill From": "",
                "Balance Total": 0.0
            }
            objects_added.append(dummy_vendor)

    print(f"CHECKPOINT: Found {len(objects_added)} new {object_mode}s to add")

    # Concurrently post all objects
    if object_mode == "Customer":
        from api.customers import customer_threadsafe
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            list(tqdm(executor.map(customer_threadsafe, objects_added), total=len(objects_added)))

    elif object_mode == "Vendor":
        from api.vendors import vendor_threadsafe
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            list(tqdm(executor.map(customer_threadsafe, objects_added), total=len(objects_added)))

    return extracted

def resolve_ids(extracted=None, object_mode=None):
    if extracted is None or object_mode is None:
        print("ERROR: No object or mode was passed into resolve function")
        return None

    if object_mode not in ["Customer", "Vendor"]:
        print("ERROR: Incorrect enum mode passed into resolve function")
        return None

    from api.retrieve import get_database
    pre_object = get_database(query_mode=object_mode)

    if pre_object is None or object_mode not in list(pre_object.keys()):
        print(f"WARNING: Please upload {object_mode}s to QBO before posting invoices")
        return None

    post_object = pre_object[object_mode]

    # pull QBO id from objects
    ids_mapping = {}
    for single in post_object:
        ids_mapping[single['DisplayName']] = single['Id']
    if len(ids_mapping.values()) != len(ids_mapping.keys()):
        print(f"ERROR: {object_mode}s does not equal ids, some other error occured")
        return extracted
    if len(list(ids_mapping.values())) == 0:
        return extracted

    print(f"CHECKPOINT: Found {len(list(ids_mapping.values()))} existing {object_mode} Ids")

    # assign each item the corresponding id
    for item_object in list(extracted.values()):
        if item_object['Name'] in list(ids_mapping.keys()):
            item_object['Id'] = ids_mapping[item_object['Name']]

    return extracted
